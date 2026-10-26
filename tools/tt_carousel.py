"""TikTok-карусель frightclub: python3 carousel.py <slug> ... (конфиги в STORIES)."""
import base64, io, pathlib, sys
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from playwright.sync_api import sync_playwright

F = pathlib.Path('/home/claude/fontdl'); D = pathlib.Path('/home/claude/car')
b = lambda p: base64.b64encode((F / p).read_bytes()).decode()
def face(fam, lat, cyr):
    return (f"@font-face{{font-family:{fam};src:url(data:font/woff2;base64,{b(lat)});unicode-range:U+0000-00FF,U+2013-2014,U+2018-201E,U+2026}}"
            f"@font-face{{font-family:{fam};src:url(data:font/woff2;base64,{b(cyr)});unicode-range:U+0400-04FF}}")
CSS = (face('T', 'alumni-sans/files/alumni-sans-latin-900-normal.woff2', 'alumni-sans/files/alumni-sans-cyrillic-900-normal.woff2') +
       face('M', 'jetbrains-mono/files/jetbrains-mono-latin-500-normal.woff2', 'jetbrains-mono/files/jetbrains-mono-cyrillic-500-normal.woff2') +
       "body{margin:0}.c{width:1080px;height:1920px;background:#0B0B0C;position:relative;overflow:hidden;font-family:M;color:#E8E2D6}"
       ".mark{position:absolute;top:150px;left:72px;right:72px;display:flex;justify-content:space-between;font-size:22px;letter-spacing:6px;text-transform:uppercase;color:#8E8A82}.mark b{color:#E8E2D6;font-weight:500}"
       ".body{font-family:T;font-size:92px;line-height:.98}.red{color:#C1121F}"
       ".small{font-size:22px;letter-spacing:5px;text-transform:uppercase;color:#8E8A82}"
       ".q{font-size:30px;letter-spacing:3px;color:#B5B0A6;text-transform:uppercase;line-height:1.6;margin-top:80px}")
logo = base64.b64encode(pathlib.Path('/home/claude/tcm/icon.png').read_bytes()).decode()

def treat_bg(path, cx=.5, blur=0, bright=1.0):
    im = Image.open(path).convert('RGB')
    w, h = im.size; tw = int(h * 1080 / 1920)
    x0 = int(w * cx - tw / 2); x0 = max(0, min(w - tw, x0))
    im = im.crop((x0, 0, x0 + tw, h)).resize((1080, 1920), Image.LANCZOS)
    im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(.72)).enhance(1.12)
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    im = ImageEnhance.Brightness(im).enhance(bright)
    a = np.asarray(im).astype(np.float32); lum = a.mean(2, keepdims=True) / 255
    a = a * (.9 + .1 * lum) + np.array([10, -2, -4]) * (1 - lum)
    buf = io.BytesIO(); Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(buf, 'JPEG', quality=94)
    return base64.b64encode(buf.getvalue()).decode()

def sliced(text, size, split=54, shift=14, line=7):
    base = f"font-family:T;font-size:{size}px;line-height:.86;color:#E8E2D6;text-transform:uppercase;white-space:pre;padding:0 .12em 0 .02em"
    return (f'<div style="position:relative;display:inline-block"><div style="{base};visibility:hidden">{text}</div>'
            f'<div style="{base};position:absolute;inset:0;clip-path:inset(-20% -10% {100-split}% -10%)">{text}</div>'
            f'<div style="{base};position:absolute;inset:0;clip-path:inset({split}% -10% -20% -10%);transform:translateX({shift}px)">{text}</div>'
            f'<div style="position:absolute;left:-24px;right:-24px;top:calc({split}% - {line/2}px);height:{line}px;background:#C1121F;transform:rotate(-1deg)"></div></div>')

def auto(big):
    lines = big.split('\n'); L = max(len(x) for x in lines)
    size = 300 if L <= 5 else int(300 * 5.6 / L)
    size = min(size, 300, int(1000 / (len(lines) * .9)))
    return size, (54 if len(lines) == 1 else int(100 / len(lines) * 1.0) if len(lines) == 2 else 36)

def build(cfg):
    out = D / cfg['slug']; out.mkdir(exist_ok=True)
    mark = f'<div class="mark"><b>frightclub</b><span>{cfg.get("rubric", "история")}</span></div>'
    img = str(D / cfg['img'])
    slides = []
    cover = treat_bg(img, cfg.get('cx', .5), 0, cfg.get('cover_bright', .62))
    L = max(len(x) for x in cfg['hook'].split('\n')); hs = min(172, int(880 / (L * .40))); hsplit = 36 if cfg['hook'].count('\n') == 2 else 50
    slides.append(f'''<div class="c"><img src="data:image/jpeg;base64,{cover}" style="position:absolute;inset:0;width:100%;height:100%">
<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,11,12,.55) 0%,rgba(11,11,12,0) 30%,rgba(11,11,12,0) 45%,rgba(11,11,12,.92) 78%,#0B0B0C 100%)"></div>
{mark}<div style="position:absolute;left:72px;right:100px;top:{cfg.get('hook_top', 1030)}px">{sliced(cfg['hook'], hs, hsplit)}
<div class="small" style="margin-top:40px">{cfg['sub']}</div></div></div>''')
    for s in cfg['slides']:
        big, body = s[0], s[1]; foot = s[2] if len(s) > 2 else ''
        size, split = auto(big)
        slides.append(f'<div class="c">{mark}<div style="position:absolute;left:72px;right:150px;top:260px;bottom:420px;display:flex;flex-direction:column;justify-content:center">'
                      f'<div>{sliced(big, size, split)}</div><div class="body" style="margin-top:70px">{body}</div>'
                      + (f'<div class="q">{foot}</div>' if foot else '') + '</div></div>')
    endbg = treat_bg(img, cfg.get('cx', .5), 26, .32)
    fsize, fsplit = auto(cfg['final_big']); fsize = min(fsize, 230)
    slides.append(f'''<div class="c"><img src="data:image/jpeg;base64,{endbg}" style="position:absolute;inset:0;width:100%;height:100%">{mark}
<div style="position:absolute;left:72px;right:120px;top:520px"><div class="body" style="font-size:92px;color:#8E8A82">{cfg['final_small']}</div>
<div style="margin-top:50px">{sliced(cfg['final_big'], fsize, fsplit)}</div></div>
<img src="data:image/png;base64,{logo}" style="position:absolute;left:72px;top:1320px;width:150px;height:150px;opacity:.85;border-radius:12px"></div>''')
    with sync_playwright() as p:
        br = p.chromium.launch(); pg = br.new_page(viewport={'width': 1080, 'height': 1920})
        for i, s in enumerate(slides, 1):
            pg.set_content(f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{s}</body></html>')
            pg.wait_for_timeout(250)
            png = out / f'{i:02d}.png'; pg.screenshot(path=str(png))
            im = Image.open(png).convert('RGB'); a = np.asarray(im).astype(np.float32)
            a += np.random.default_rng(i).normal(0, 6, a.shape[:2])[..., None]
            Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(out / f'{i:02d}.jpg', quality=93, subsampling=0); png.unlink()
        br.close()
    n = len(slides); cols = 5; rows = (n + cols - 1) // cols
    sheet = Image.new('RGB', (cols * 216, rows * 384), '#333')
    for i in range(n): sheet.paste(Image.open(out / f'{i+1:02d}.jpg').resize((216, 384)), ((i % cols) * 216, (i // cols) * 384))
    sheet.save(D / f'sheet-{cfg["slug"]}.jpg', quality=85)
    return n

if __name__ == '__main__':
    from stories import STORIES
    for slug in sys.argv[1:] or list(STORIES):
        print(slug, build(STORIES[slug]))
