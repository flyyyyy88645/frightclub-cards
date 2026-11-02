#!/usr/bin/env python3
"""
Проверка поста frightclub перед превью Тимуру — формальные правила канала, без ИИ.

  python3 tools/check_post.py post.txt [--platform tg|tiktok] [--rubric история] [--image URL] [--facts-checked] [--json]
  cat post.txt | python3 tools/check_post.py - --platform tg

ОШИБКА (exit 1) — пост в таком виде не отправлять, исправить.
ВНИМАНИЕ        — посмотреть глазами; может быть нормально.
Последняя строка вывода — готовая строка «✅ проверено: …» для превью (только если ошибок нет).

Факты (даты, RT, режиссёр, русское название) скрипт не проверяет — их сверять заново
инструментами (tmdb_details, movie_ratings), а не по памяти.
"""
import argparse, json, re, sys
from html.parser import HTMLParser

CAPTION_LIMIT = 1024          # подпись к фото в Telegram
TIKTOK_LIMIT = 2200           # описание в TikTok
ALLOWED_TAGS = {"b", "strong", "i", "em", "u", "ins", "s", "strike", "del", "a", "code", "pre",
                "tg-spoiler", "span", "blockquote"}

# (регэксп, сообщение) — нарушают правила канала
BANNED = [
    (r"х[эе]лл?оуин|halloween", "Хэллоуин в тексте — запрещено"),
    (r"frightclub", "слово frightclub внутри текста поста — запрещено"),
    (r"источник\s*:\s*tmdb|данные\s+tmdb", "подпись «источник: TMDB» — запрещено"),
    (r"вспомнишь через неделю|финал (ты )?(будешь )?вспомина", "клише «финал вспомнишь через неделю»"),
    (r"\*\*|__|^#{1,3}\s|\[[^\]]+\]\(https?://", "markdown вместо HTML (**, __, #, [текст](ссылка)) — в Telegram покажется как есть"),
]
# (регэксп, сообщение) — частые правки Тимура, проверить глазами
WARN = [
    (r"\bкринж", "«кринж» — устаревший сленг, Тимур такое убирает"),
    (r"\bв канне\b", "«в Канне» → «в Каннах»"),
    (r"фл[еэа]н[аэ]ган|фланаган", "Flanagan пишем «Флэнеган»"),
    (r"\bманборг", "Manborg — «Мэнборг»"),
    (r"картонн\w* персонаж", "резкий ярлык («картонные персонажи») — Тимур смягчает"),
    (r"https?://", "ссылка в посте — источники в посты не ставим"),
    (r"18\+|очень тяж[её]лый фильм(?!\. детям)", "предупреждение о тяжёлом фильме — только строкой «⚠️ очень тяжёлый фильм. детям и впечатлительным — мимо»"),
    (r"сня(л|ла|ли)\s+(это\s+)?на\s+\d+\s+минут", "хронометраж: «фильм идёт N минут»"),
]
KILL_RE = re.compile(r"\b(убийств\w*|убийц\w*|уби(л|ла|ли|ть|ваю\w*|вает\w*|т)\b)", re.I)
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF☀-➿️‍]+")


class TagCheck(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.problems = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in ALLOWED_TAGS:
            self.problems.append(f"тег <{tag}> Telegram не понимает")
        if tag == "a" and not dict(attrs).get("href"):
            self.problems.append("<a> без href")
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.stack:
            while self.stack and self.stack[-1] != tag:
                self.problems.append(f"<{self.stack.pop()}> не закрыт")
            self.stack.pop()
        else:
            self.problems.append(f"лишний </{tag}>")

    def close(self):
        super().close()
        self.problems += [f"<{t}> не закрыт" for t in self.stack]


def tg_len(text):
    """Длина так, как считает Telegram: без тегов, в UTF-16 (эмодзи весят больше)."""
    plain = re.sub(r"<[^>]+>", "", text)
    plain = plain.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&amp;", "&")
    return len(plain.encode("utf-16-le")) // 2, plain


def check(text, platform="tg", rubric="", image="", facts=False):
    errors, warns, passed = [], [], []
    text = text.strip("\n")
    n, plain = tg_len(text)
    low = plain.lower()

    # длина
    limit = TIKTOK_LIMIT if platform == "tiktok" else CAPTION_LIMIT
    if n > limit:
        errors.append(f"длина {n}/{limit} — надо сократить на {n - limit}")
    else:
        passed.append(f"{n}/{limit} симв.")
        if platform == "tg" and n > limit - 15:
            warns.append(f"длина {n}/{limit} — впритык, любая правка Тимура может не влезть")

    # разметка
    if platform == "tg":
        tc = TagCheck(); tc.feed(text); tc.close()
        errors += [f"разметка: {p}" for p in dict.fromkeys(tc.problems)]
        if not tc.problems:
            passed.append("разметка ок")
        if re.search(r"&(?!(lt|gt|amp|quot);)", text):
            errors.append("голый & — в HTML-режиме Telegram отвергнет пост (писать &amp;)")
        if re.search(r"<(?![/a-z])", text):
            errors.append("голый < — Telegram примет за тег (писать &lt;)")
        if not re.match(r"\s*<b>", text):
            warns.append("заголовок не в <b> в начале поста")

    # запрещённое
    hits = [msg for rx, msg in BANNED if re.search(rx, plain if "markdown" not in msg else text, re.I | re.M)]
    errors += hits
    if not hits:
        passed.append("без запрещённого")
    warns += [msg for rx, msg in WARN if re.search(rx, plain, re.I)]

    # TikTok: цензура «уб*йство»
    if platform == "tiktok":
        k = sorted({m.group(0) for m in KILL_RE.finditer(plain)})
        if k:
            errors.append("TikTok: «" + "», «".join(k) + "» — писать через звёздочку (уб*йство, уб*л, уб*йца)")

    # стиль канала
    emojis = len(EMOJI_RE.findall(plain.replace("⚠️", "")))
    if platform == "tg" and not (1 <= emojis <= 4):
        warns.append(f"эмодзи: {emojis} (в канале 2–3 на пост)")
    body_lines = [l for l in plain.split("\n")[1:] if l.strip()]
    caps = [l for l in body_lines if re.match(r"\s*[«\"(]?[А-ЯЁ][а-яё]", l)]
    if platform == "tg" and len(caps) > max(1, len(body_lines) // 3):
        warns.append("много строк с большой буквы — в канале пишем строчными")
    if platform == "tg" and "истор" not in rubric.lower() and "?" not in plain.split("\n")[-1] \
            and not re.search(r"\?\s*\S{0,4}\s*$", plain.strip()):
        warns.append("в конце нет вопроса к подписчикам")
    if plain.count("«") != plain.count("»"):
        warns.append("кавычки «» не парные")
    if re.search(r"(\S)\1{4,}", plain):
        warns.append("подозрительный повтор символов")

    # карточка
    if image:
        if "raw.githubusercontent.com" in image and re.search(r"/main/|/master/", image):
            errors.append("ссылка на карточку через main — нужен хэш коммита (Telegram кэширует старую картинку)")
        elif "raw.githubusercontent.com" in image and not re.search(r"/[0-9a-f]{7,40}/", image):
            warns.append("в ссылке на карточку не видно хэша коммита")
        else:
            passed.append("карточка по хэшу")

    ok = not errors
    summary = ("✅ проверено: " + " · ".join(passed + (["факты сверены заново"] if facts else [])) +
               ("" if facts else " · ⚠️ факты не сверены")) if ok else ""
    return {"ok": ok, "length": n, "errors": errors, "warnings": warns, "summary": summary}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="файл с текстом поста или - для stdin")
    ap.add_argument("--platform", choices=["tg", "tiktok"], default="tg")
    ap.add_argument("--rubric", default="")
    ap.add_argument("--image", default="", help="ссылка на карточку")
    ap.add_argument("--facts-checked", action="store_true",
                    help="факты действительно сверены инструментами (tmdb_details, movie_ratings) — иначе в итоге будет пометка")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    text = sys.stdin.read() if a.file == "-" else open(a.file, encoding="utf-8").read()
    r = check(text, a.platform, a.rubric, a.image, a.facts_checked)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        for e in r["errors"]:
            print("ОШИБКА:", e)
        for w in r["warnings"]:
            print("ВНИМАНИЕ:", w)
        print(r["summary"] or f"❌ не прошло: {len(r['errors'])} ошиб.")
    sys.exit(0 if r["ok"] else 1)


if __name__ == "__main__":
    main()
