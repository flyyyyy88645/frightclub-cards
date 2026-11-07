# Карточки 1080×1350 — код и параметры

> Справочник скилла horror-news-digest. Правила работы — только в скилле; здесь — данные и код. Правится коммитом без карточки скилла.
> Читать перед любой карточкой (правила раскладки — скилл, раздел 4).

**Быстрый путь (5.11.2026): `python3 tools/card.py --help`** — та же раскладка одной командой, шрифты качает сам, `--variants` даёт лист обложек. Код ниже — справочно и для нестандартных раскладок.

Сборка вручную (Playwright уже есть в окружении; шрифты — с npm):

```bash
mkdir -p /home/claude/fontdl && cd /home/claude/fontdl
for p in alumni-sans jetbrains-mono; do npm pack @fontsource/$p >/dev/null 2>&1; mkdir -p $p && tar xzf fontsource-$p-*.tgz -C $p --strip-components=1; done
```

```python
import base64, io, pathlib, numpy as np
from PIL import Image, ImageEnhance
from playwright.sync_api import sync_playwright
F=pathlib.Path('/home/claude/fontdl'); b=lambda p: base64.b64encode((F/p).read_bytes()).decode()
def face(fam,lat,cyr): return (f"@font-face{{font-family:{fam};src:url(data:font/woff2;base64,{b(lat)});unicode-range:U+0000-00FF,U+2013-2014}}"
  f"@font-face{{font-family:{fam};src:url(data:font/woff2;base64,{b(cyr)});unicode-range:U+0400-04FF}}")
CSS=(face('T','alumni-sans/files/alumni-sans-latin-900-normal.woff2','alumni-sans/files/alumni-sans-cyrillic-900-normal.woff2')+
     face('M','jetbrains-mono/files/jetbrains-mono-latin-500-normal.woff2','jetbrains-mono/files/jetbrains-mono-cyrillic-500-normal.woff2')+
     "body{margin:0}.card{width:1080px;height:1350px;background:#0B0B0C;position:relative;overflow:hidden;font-family:M;color:#E8E2D6}"
     ".mark{position:absolute;top:44px;left:56px;right:56px;display:flex;justify-content:space-between;font-size:19px;letter-spacing:5px;text-transform:uppercase;color:#8E8A82}.mark b{color:#E8E2D6;font-weight:500}")
def treat(path, crop=None):
    im=Image.open(path).convert('RGB')
    if crop: im=im.crop(crop)
    im=ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(.72)).enhance(1.12)
    a=np.asarray(im).astype(np.float32); lum=a.mean(2,keepdims=True)/255
    a=a*(.9+.1*lum)+np.array([10,-2,-4])*(1-lum); a+=np.random.default_rng(1).normal(0,7,a.shape[:2])[...,None]
    im=Image.fromarray(np.clip(a,0,255).astype(np.uint8)); buf=io.BytesIO(); im.save(buf,'JPEG',quality=95)
    return base64.b64encode(buf.getvalue()).decode(), im.size
def sliced(text,size,split=54,shift=12,line=6):
    base=f"font-family:T;font-size:{size}px;line-height:.85;color:#E8E2D6;text-transform:uppercase;white-space:pre;padding:0 .12em 0 .02em"
    return (f'<div style="position:relative;display:inline-block"><div style="{base};visibility:hidden">{text}</div>'
      f'<div style="{base};position:absolute;inset:0;clip-path:inset(-20% -10% {100-split}% -10%)">{text}</div>'
      f'<div style="{base};position:absolute;inset:0;clip-path:inset({split}% -10% -20% -10%);transform:translateX({shift}px)">{text}</div>'
      f'<div style="position:absolute;left:-20px;right:-20px;top:calc({split}% - {line/2}px);height:{line}px;background:#C1121F;transform:rotate(-1deg)"></div></div>')
def card(img, rubric, title, sub, rt, title_size=150, split=54, img_box=None, crop=None, ph=800, pos="50% 50%"):
    data,(w,h)=treat(img,crop)
    if img_box is None:  # вертикальный постер по центру
        pw=int(w*ph/h); box=f"top:108px;left:50%;transform:translateX(-50%) rotate(-1.2deg);width:{pw}px;height:{ph}px"
    else: box=img_box      # для кадров: задать вручную, напр. "top:120px;left:56px;width:968px;height:930px;transform:rotate(-.8deg)"
    rtb='' if rt is None else f'''<div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px"><span style="font-size:16px;letter-spacing:4px;text-transform:uppercase;color:#8E8A82">критики rt</span>
<span style="font-family:T;font-size:150px;line-height:.85">{rt}</span></div>'''
    return f'''<div class="card"><div class="mark"><b>frightclub</b><span>{rubric}</span></div>
<div style="position:absolute;{box};box-shadow:0 30px 60px rgba(0,0,0,.6),0 0 0 1px #2a2a2c"><img src="data:image/jpeg;base64,{data}" style="width:100%;height:100%;display:block;object-fit:cover;object-position:{pos}"></div>
<div style="position:absolute;left:56px;right:56px;bottom:64px;display:flex;justify-content:space-between;align-items:flex-end;gap:24px">
<div>{sliced(title,title_size,split)}<div style="margin-top:18px;font-size:19px;letter-spacing:3px;text-transform:uppercase;color:#8E8A82">{sub}</div></div>
{rtb}</div></div>'''
def render(html, out):
    with sync_playwright() as p:
        br=p.chromium.launch(); pg=br.new_page(viewport={'width':1080,'height':1350},device_scale_factor=1.5)
        pg.set_content(f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{html}</body></html>'); pg.wait_for_timeout(400)
        pg.screenshot(path=out+'.png'); br.close()
    im=Image.open(out+'.png').convert('RGB'); a=np.asarray(im).astype(np.float32)
    a+=np.random.default_rng(3).normal(0,5,a.shape[:2])[...,None]
    Image.fromarray(np.clip(a,0,255).astype(np.uint8)).save(out+'.jpg',quality=93,subsampling=0)
    im.resize((360,450)).save(out+'_prev.png')
```

## Параметры раскладки

- Длинный заголовок: уменьшай `title_size`, разбивай `\n` на 2–3 строки. `split` (место надреза, %): 2 строки ≈ 50, 3 строки ≈ 68 (между 2-й и 3-й; проверено на «КАК ФЛЭНЕГАН / ПЕРЕПРИДУМАЛ / ХОРРОР-СЕРИАЛЫ», size 128, кадр 968×745).
- Без рейтинга — `rt=None`.
- Горизонтальный кадр для «хоррора на вечер»: `img_box` `top:120px;left:56px;width:968px`, высота **930px при однострочном заголовке**, **850px при двухстрочном** (title_size 120, split 50) — так нет пустоты над заголовком (проверено 2.11 на 6 карточках). `pos` — сдвиг кадрирования (`"62% 50%"`), чтобы лица не резались.
- «История» с 3-строчным заголовком — высота кадра 745–820.
- Примеры кропа надписи на постере: Smile — кроп по лицу, надпись SMILE отрезана; Brightburn (2.11) — `crop=(0,40,1012,1230)`, `ph=930`.
- Лист-превью пачки: 3×2 по 360×450 (`_prev.png` из `render`).

## «Почему страшно» — шаблон (утверждён 7.11.2026)

`python3 tools/why_card.py <кадр> "<ТЕМА>" "<номер>" cards/<дата>-why-<тема>` — раскладка как у «пустого кадра» (31.10): справа вверху «разбор», широкий кадр 972×418 по центру, крупно «ПОЧЕМУ СТРАШНО» с надрезом (170px), под ним тема **красным** (95.5px), номер части серии — тоже красным, тем же кеглем (решение 7.11). Под темой мелко серым — из какого фильма кадр (7-й аргумент, «кадр: название · original · год»). Сетка — как у остальных обложек (card.py): кадр 968 шириной от top 120, текстовый блок прижат к низу (bottom 64), подпись кадра 18px под темой; кадр по умолчанию 968×800. Без рейтинга и подписи «кадр: …». Размеры не менять.
