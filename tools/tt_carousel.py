import base64, io, pathlib, sys
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from playwright.sync_api import sync_playwright

F = pathlib.Path('/home/claude/fontdl'); D = pathlib.Path('/home/claude/tcm'); OUT = D / 'slides'; OUT.mkdir(exist_ok=True)
b = lambda p: base64.b64encode((F / p).read_bytes()).decode()
def face(fam, lat, cyr):
    return (f"@font-face{{font-family:{fam};src:url(data:font/woff2;base64,{b(lat)});unicode-range:U+0000-00FF,U+2013-2014,U+2018-201E,U+2026}}"
            f"@font-face{{font-family:{fam};src:url(data:font/woff2;base64,{b(cyr)});unicode-range:U+0400-04FF}}")
CSS = (face('T', 'alumni-sans/files/alumni-sans-latin-900-normal.woff2', 'alumni-sans/files/alumni-sans-cyrillic-900-normal.woff2') +
       face('M', 'jetbrains-mono/files/jetbrains-mono-latin-500-normal.woff2', 'jetbrains-mono/files/jetbrains-mono-cyrillic-500-normal.woff2') +
       "body{margin:0}.c{width:1080px;height:1920px;background:#0B0B0C;position:relative;overflow:hidden;font-family:M;color:#E8E2D6}"
       ".mark{position:absolute;top:150px;left:72px;right:72px;display:flex;justify-content:space-between;font-size:22px;letter-spacing:6px;text-transform:uppercase;color:#8E8A82}.mark b{color:#E8E2D6;font-weight:500}"
       ".body{font-family:T;font-size:92px;line-height:.98;text-transform:none}.red{color:#C1121F}"
       ".small{font-size:22px;letter-spacing:5px;text-transform:uppercase;color:#8E8A82}")

def treat_bg(path, blur=0, bright=1.0):
    im = Image.open(path).convert('RGB')
    w, h = im.size; tw = int(h * 1080 / 1920)
    x0 = int(w * 0.53 - tw / 2); x0 = max(0, min(w - tw, x0))
    im = im.crop((x0, 0, x0 + tw, h)).resize((1080, 1920), Image.LANCZOS)
    im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(.72)).enhance(1.12)
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    im = ImageEnhance.Brightness(im).enhance(bright)
    a = np.asarray(im).astype(np.float32); lum = a.mean(2, keepdims=True) / 255
    a = a * (.9 + .1 * lum) + np.array([10, -2, -4]) * (1 - lum)
    buf = io.BytesIO(); Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(buf, 'JPEG', quality=94)
    return base64.b64encode(buf.getvalue()).decode()

def sliced(text, size, split=54, shift=14, line=7, color='#E8E2D6'):
    base = f"font-family:T;font-size:{size}px;line-height:.86;color:{color};text-transform:uppercase;white-space:pre;padding:0 .12em 0 .02em"
    return (f'<div style="position:relative;display:inline-block"><div style="{base};visibility:hidden">{text}</div>'
            f'<div style="{base};position:absolute;inset:0;clip-path:inset(-20% -10% {100-split}% -10%)">{text}</div>'
            f'<div style="{base};position:absolute;inset:0;clip-path:inset({split}% -10% -20% -10%);transform:translateX({shift}px)">{text}</div>'
            f'<div style="position:absolute;left:-24px;right:-24px;top:calc({split}% - {line/2}px);height:{line}px;background:#C1121F;transform:rotate(-1deg)"></div></div>')

eye = str(D / 'eye.jpg')
logo = base64.b64encode((D / 'icon.png').read_bytes()).decode()
RUB = 'история'
mark = f'<div class="mark"><b>frightclub</b><span>{RUB}</span></div>'

def text_slide(big, size, body, split=54, foot=''):
    return (f'<div class="c">{mark}'
            f'<div style="position:absolute;left:72px;right:150px;top:260px;bottom:420px;display:flex;flex-direction:column;justify-content:center"><div>{sliced(big, size, split)}</div>'
            f'<div class="body" style="margin-top:70px">{body}</div>'
            f'{foot}</div></div>')

cover_bg = treat_bg(eye, 0, .62)
end_bg = treat_bg(eye, 26, .32)
slides = []
# 1 — обложка
slides.append(f'''<div class="c"><img src="data:image/jpeg;base64,{cover_bg}" style="position:absolute;inset:0;width:100%;height:100%">
<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,11,12,.55) 0%,rgba(11,11,12,0) 30%,rgba(11,11,12,0) 45%,rgba(11,11,12,.92) 78%,#0B0B0C 100%)"></div>
{mark}
<div style="position:absolute;left:72px;right:120px;top:1030px">{sliced("кожаное лицо —\nне главный\nзлодей", 172, 36)}
<div class="small" style="margin-top:40px">техасская резня бензопилой · 1974</div></div></div>''')
# 2
slides.append(text_slide('1972', 300,
    '«глубокую глотку» снимают за&nbsp;<span class="red">$22&nbsp;тыс.</span><br><br>а собирает она, по&nbsp;разным оценкам, <span class="red">$30–50&nbsp;млн</span>'))
# 3
slides.append(text_slide('семья\nколомбо', 220,
    'прокатывает фильм bryanston луиса перайно. его отец — человек мафиозной семьи коломбо<br><br>деньги надо куда-то вкладывать. и&nbsp;перайно идёт в&nbsp;«нормальное» кино', split=50))
# 4
slides.append(text_slide('1974', 300,
    'молодой тоуб хупер снимает за&nbsp;копейки фильм про&nbsp;семью каннибалов<br><br>брать его в&nbsp;прокат не&nbsp;хочет никто. кроме bryanston'))
# 5
slides.append(text_slide('$225 000\n+ 35%', 220,
    'столько создателям пообещали за&nbsp;фильм: деньги и&nbsp;треть прибыли<br><br>звучит как&nbsp;отличная сделка', split=50))
# 6
slides.append(text_slide('$30 млн+', 240,
    'фильм продаёт <span class="red">16,5&nbsp;млн</span> билетов и&nbsp;становится 12-м по&nbsp;сборам за&nbsp;1974&nbsp;год'))
# 7
slides.append(text_slide('$8 100', 300,
    'столько осталось после мафиозной бухгалтерии<br><br>на&nbsp;всю команду из&nbsp;<span class="red">20&nbsp;человек</span>',
    foot='<div class="small" style="margin-top:80px;line-height:1.6;font-size:30px;letter-spacing:3px;color:#B5B0A6">«мы заключили сделку с дьяволом»<br>— производственный менеджер фильма</div>'))
# 8
slides.append(text_slide('финал', 300,
    'bryanston обанкротилась, братьев перайно осудили<br><br>а&nbsp;свою долю команда начала получать только в&nbsp;<span class="red">1983-м</span>, когда права перешли к&nbsp;new line cinema'))
# 9 — финал
slides.append(f'''<div class="c"><img src="data:image/jpeg;base64,{end_bg}" style="position:absolute;inset:0;width:100%;height:100%">{mark}
<div style="position:absolute;left:72px;right:120px;top:560px"><div class="body" style="font-size:96px;color:#8E8A82">главный злодей этой&nbsp;истории —</div>
<div style="margin-top:50px">{sliced("дистри-\nбьютор", 230, 50)}</div></div>
<img src="data:image/png;base64,{logo}" style="position:absolute;left:72px;top:1300px;width:150px;height:150px;opacity:.85;border-radius:12px"></div>''')

with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={'width': 1080, 'height': 1920})
    for i, s in enumerate(slides, 1):
        pg.set_content(f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{s}</body></html>')
        pg.wait_for_timeout(300)
        png = OUT / f'{i:02d}.png'; pg.screenshot(path=str(png))
        im = Image.open(png).convert('RGB'); a = np.asarray(im).astype(np.float32)
        a += np.random.default_rng(i).normal(0, 6, a.shape[:2])[..., None]
        Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(OUT / f'{i:02d}.jpg', quality=93, subsampling=0); png.unlink()
    br.close()
# contact sheet
ims = [Image.open(OUT / f'{i:02d}.jpg').resize((270, 480)) for i in range(1, len(slides) + 1)]
sheet = Image.new('RGB', (270 * 5 + 40, 480 * 2 + 30), '#333')
for k, im in enumerate(ims): sheet.paste(im, (10 + (k % 5) * 280 - 10 * (k % 5) + (k % 5) * 0, 10 + (k // 5) * 490))
sheet.save(D / 'sheet.jpg', quality=88)
print('ok', len(slides))
