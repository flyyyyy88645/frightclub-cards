#!/usr/bin/env python3
"""Готовит scheduled task для поста в @frightclub88 из одобренного текста — без ручного копирования.

  python3 tools/schedule_prompt.py post.txt --image <raw-ссылка с хэшем> \
      --rubric история --label A24 --when "2026-11-06 13:00"

--when — время МСК; задача ставится на 3 минуты раньше (холодный старт коннектора).
Печатает JSON {name, run_once_at, prompt} — его поля идут в create_trigger / update_trigger как есть.
Отказывает, если ссылка на карточку не по хэшу коммита или время уже прошло.
"""
import argparse, datetime as dt, json, re, sys

TEMPLATE = """Опубликуй один заранее одобренный пользователем (Тимур) пост в его Telegram-канал @frightclub88 (рубрика «{rubric}»). Тимур сам попросил поставить эту публикацию на это время и одобрил текст и картинку — переспрашивать не нужно, но опубликуй ровно один раз и ровно этот контент.

ДОЖДИСЬ КОННЕКТОРА. Сервер frightclubtg просыпается не сразу (холодный старт): в первые минуты сессии его инструментов может не быть. Это НЕ сбой. Если ToolSearch не нашёл mcp__frightclubtg__tg_send_photo: выполни в Bash `sleep 60`, затем RefreshMcpTools и снова ToolSearch. Повторяй до 6 раз. Только если после всех попыток коннектора нет — отправь PushNotification «пост «{rubric}: {label}» не опубликован: коннектор frightclubtg не подключился» и закончи.

Как: загрузи инструмент через ToolSearch запросом "select:mcp__frightclubtg__tg_send_photo" и вызови его с аргументами:
- chat_id: "@frightclub88"
- photo: "{image}"
- parse_mode: "HTML"
- caption: текст между строками ===НАЧАЛО=== и ===КОНЕЦ=== без изменений (с переносами строк и тегами <b>), сами эти строки не включай

===НАЧАЛО===
{caption}
===КОНЕЦ===

Если вызов вернул успех — коротко сообщи через SendUserMessage «Опубликовал «{rubric}»: {label}». Если ошибка — не повторяй больше одного раза; сообщи Тимуру текст ошибки."""

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('post'); ap.add_argument('--image', required=True)
    ap.add_argument('--rubric', required=True); ap.add_argument('--label', required=True)
    ap.add_argument('--when', required=True, help='"YYYY-MM-DD HH:MM" по Москве')
    a = ap.parse_args()
    if not re.search(r'frightclub-cards/[0-9a-f]{40}/', a.image):
        if re.search(r'frightclub-cards/[0-9a-f]{7,39}/', a.image):
            sys.exit('ОШИБКА: в ссылке короткий хэш — нужен полный, 40 символов (git rev-parse HEAD)')
        sys.exit('ОШИБКА: ссылка на карточку должна быть с полным хэшем коммита (40 символов), не main')
    caption = open(a.post, encoding='utf-8').read().strip()
    if len(caption.encode('utf-16-le')) // 2 > 1024 + 2 * caption.count('<'):  # грубая страховка; точная — check_post.py
        print('ВНИМАНИЕ: подпись может быть длиннее 1024 — прогони check_post.py', file=sys.stderr)
    msk = dt.datetime.strptime(a.when, '%Y-%m-%d %H:%M').replace(tzinfo=dt.timezone(dt.timedelta(hours=3)))
    run = (msk - dt.timedelta(minutes=3)).astimezone(dt.timezone.utc)
    if run <= dt.datetime.now(dt.timezone.utc):
        sys.exit(f'ОШИБКА: {run:%Y-%m-%d %H:%M} UTC уже прошло')
    print(json.dumps({
        'name': f'frightclub · {a.rubric}: {a.label} {msk.day}.{msk.month:02d} {msk:%H:%M}',
        'run_once_at': run.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'prompt': TEMPLATE.format(rubric=a.rubric, label=a.label, image=a.image, caption=caption),
    }, ensure_ascii=False, indent=1))

if __name__ == '__main__':
    main()
