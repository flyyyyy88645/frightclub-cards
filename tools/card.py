#!/usr/bin/env python3
"""Карточка frightclub 1080×1350 одной командой (раскладка — docs-skill/cards.md).

Одна карточка (горизонтальный кадр):
  python3 tools/card.py --img still.jpg --rubric история --title "КАК A24|СТАЛ БРЕНДОМ" \
      --sub "кадр: реинкарнация · hereditary · 2018 · ари астер" --out cards/2026-11-05-history-a24

Вертикальный постер по центру:          --layout poster [--ph 800] [--crop 0,40,1012,1230]
С рейтингом:                             --rt 78%
Варианты обложки листом (одна раскладка, разные кадры):
  python3 tools/card.py --variants a.jpg::"кадр: …" b.jpg::"кадр: …" --rubric история \
      --title "…|…" --out /tmp/v      →  /tmp/v-1.jpg, /tmp/v-2.jpg … и /tmp/v-sheet.png

«|» в заголовке — перенос строки. Размер, надрез и высоту кадра скрипт подбирает
по числу строк (1 стр.: 150/54/930, 2: 120/50/850, 3: 110/68/780) — можно переопределить.
Шрифты скачиваются с npm в ~/fontdl при первом запуске.
Результат: <out>.jpg (в канал), <out>_prev.png (360×450, для листа).
"""
import argparse, base64, io, pathlib, subprocess, sys
import numpy as np
from PIL import Image, ImageEnhance

F = pathlib.Path.home() / 'fontdl'

def ensure_fonts():
    for p in ('alumni-sans', 'jetbrains-mono'):
        if (F / p / 'files').exists():
            continue
        F.mkdir(parents=True, exist_ok=True)
        subprocess.run(f'npm pack @fontsource/{p} >/dev/null 2>&1 && mkdir -p {p} && tar xzf fontsource-{p}-*.tgz -C {p} --strip-components=1',
                       shell=True, cwd=F, check=True)

def b64(p): return base64.b64encode((F / p).read_bytes()).decode()

def face(fam, lat, cyr):
    return (f"@font-face{{font-family:{fam};src:url(data:font/woff2;base64,{b64(lat)});unicode-range:U+0000-00FF,U+2013-2014}}"
            f"@font-face{{font-family:{fam};src:url(data:font/woff2;base64,{b64(cyr)});unicode-range:U+0400-04FF}}")

def css():
    return (face('T', 'alumni-sans/files/alumni-sans-latin-900-normal.woff2', 'alumni-sans/files/alumni-sans-cyrillic-900-normal.woff2') +
            face('M', 'jetbrains-mono/files/jetbrains-mono-latin-500-normal.woff2', 'jetbrains-mono/files/jetbrains-mono-cyrillic-500-normal.woff2') +
            "body{margin:0}.card{width:1080px;height:1350px;background:#0B0B0C;position:relative;overflow:hidden;font-family:M;color:#E8E2D6}"
            ".mark{position:absolute;top:44px;left:56px;right:56px;display:flex;justify-content:space-between;font-size:19px;letter-spacing:5px;text-transform:uppercase;color:#8E8A82}.mark b{color:#E8E2D6;font-weight:500}")

def treat(path, crop=None):
    im = Image.open(path).convert('RGB')
    if crop: im = im.crop(crop)
    im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(.72)).enhance(1.12)
    a = np.asarray(im).astype(np.float32); lum = a.mean(2, keepdims=True) / 255
    a = a * (.9 + .1 * lum) + np.array([10, -2, -4]) * (1 - lum)
    a += np.random.default_rng(1).normal(0, 7, a.shape[:2])[..., None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); buf = io.BytesIO(); im.save(buf, 'JPEG', quality=95)
    return base64.b64encode(buf.getvalue()).decode(), im.size

def sliced(text, size, split=54, shift=12, line=6):
    base = f"font-family:T;font-size:{size}px;line-height:.85;color:#E8E2D6;text-transform:uppercase;white-space:pre;padding:0 .12em 0 .02em"
    return (f'<div style="position:relative;display:inline-block"><div style="{base};visibility:hidden">{text}</div>'
            f'<div style="{base};position:absolute;inset:0;clip-path:inset(-20% -10% {100-split}% -10%)">{text}</div>'
            f'<div style="{base};position:absolute;inset:0;clip-path:inset({split}% -10% -20% -10%);transform:translateX({shift}px)">{text}</div>'
            f'<div style="position:absolute;left:-20px;right:-20px;top:calc({split}% - {line/2}px);height:{line}px;background:#C1121F;transform:rotate(-1deg)"></div></div>')

def card_html(img, rubric, title, sub, rt=None, size=150, split=54, layout='frame', h=930, ph=800, crop=None, pos='50% 50%'):
    data, (w, hh) = treat(img, crop)
    if layout == 'poster':
        pw = int(w * ph / hh); box = f"top:108px;left:50%;transform:translateX(-50%) rotate(-1.2deg);width:{pw}px;height:{ph}px"
    else:
        box = f"top:120px;left:56px;width:968px;height:{h}px;transform:rotate(-.8deg)"
    rtb = '' if not rt else (f'<div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px"><span style="font-size:16px;letter-spacing:4px;text-transform:uppercase;color:#8E8A82">критики rt</span>'
                             f'<span style="font-family:T;font-size:150px;line-height:.85">{rt}</span></div>')
    return (f'<div class="card"><div class="mark"><b>frightclub</b><span>{rubric}</span></div>'
            f'<div style="position:absolute;{box};box-shadow:0 30px 60px rgba(0,0,0,.6),0 0 0 1px #2a2a2c"><img src="data:image/jpeg;base64,{data}" style="width:100%;height:100%;display:block;object-fit:cover;object-position:{pos}"></div>'
            f'<div style="position:absolute;left:56px;right:56px;bottom:64px;display:flex;justify-content:space-between;align-items:flex-end;gap:24px">'
            f'<div>{sliced(title, size, split)}<div style="margin-top:18px;font-size:19px;letter-spacing:3px;text-transform:uppercase;color:#8E8A82">{sub}</div></div>{rtb}</div></div>')

def render_many(items):
    """items: [(html, out_stem)] — один запуск браузера на всю пачку."""
    from playwright.sync_api import sync_playwright
    style = css()
    with sync_playwright() as p:
        br = p.chromium.launch(); pg = br.new_page(viewport={'width': 1080, 'height': 1350}, device_scale_factor=1.5)
        for html, out in items:
            pg.set_content(f'<!doctype html><html><head><meta charset="utf-8"><style>{style}</style></head><body>{html}</body></html>')
            pg.wait_for_timeout(400); pg.screenshot(path=out + '.png')
        br.close()
    for _, out in items:
        im = Image.open(out + '.png').convert('RGB'); a = np.asarray(im).astype(np.float32)
        a += np.random.default_rng(3).normal(0, 5, a.shape[:2])[..., None]
        Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(out + '.jpg', quality=93, subsampling=0)
        im.resize((360, 450)).save(out + '_prev.png'); pathlib.Path(out + '.png').unlink()

def sheet(prevs, out, cols=3):
    rows = (len(prevs) + cols - 1) // cols
    S = Image.new('RGB', (cols * 380 - 20, rows * 470 - 20), '#222')
    for i, p in enumerate(prevs):
        S.paste(Image.open(p), ((i % cols) * 380, (i // cols) * 470))
    S.save(out)

DEFAULTS = {1: (150, 54, 930), 2: (120, 50, 850), 3: (110, 68, 780)}

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--img'); ap.add_argument('--sub', default='')
    ap.add_argument('--variants', nargs='+', help='путь::подпись для каждого варианта')
    ap.add_argument('--rubric', required=True); ap.add_argument('--title', required=True)
    ap.add_argument('--rt'); ap.add_argument('--out', required=True)
    ap.add_argument('--layout', choices=['frame', 'poster'], default='frame')
    ap.add_argument('--size', type=int); ap.add_argument('--split', type=int); ap.add_argument('--h', type=int)
    ap.add_argument('--ph', type=int, default=800); ap.add_argument('--pos', default='50% 50%')
    ap.add_argument('--crop', help='x0,y0,x1,y1')
    a = ap.parse_args()
    ensure_fonts()
    title = a.title.replace('|', '\n')
    n = min(title.count('\n') + 1, 3)
    size, split, h = a.size or DEFAULTS[n][0], a.split or DEFAULTS[n][1], a.h or DEFAULTS[n][2]
    crop = tuple(int(x) for x in a.crop.split(',')) if a.crop else None
    kw = dict(rt=a.rt, size=size, split=split, layout=a.layout, h=h, ph=a.ph, crop=crop, pos=a.pos)
    if a.variants:
        items = []
        for i, v in enumerate(a.variants, 1):
            img, _, sub = v.partition('::')
            items.append((card_html(img, a.rubric, title, sub or a.sub, **kw), f'{a.out}-{i}'))
        render_many(items); sheet([o + '_prev.png' for _, o in items], a.out + '-sheet.png')
        print('\n'.join(o + '.jpg' for _, o in items)); print(a.out + '-sheet.png')
    else:
        if not a.img: sys.exit('нужен --img или --variants')
        render_many([(card_html(a.img, a.rubric, title, a.sub, **kw), a.out)])
        print(a.out + '.jpg'); print(a.out + '_prev.png')

if __name__ == '__main__':
    main()
