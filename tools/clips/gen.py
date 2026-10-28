import base64, pathlib, re, sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from data import CLIPS, RU
from playwright.sync_api import sync_playwright

F = pathlib.Path('/home/claude/fontdl')
b = lambda p: base64.b64encode((F / p).read_bytes()).decode()
def face(fam, lat, cyr):
    return (f"@font-face{{font-family:{fam};src:url(data:font/woff2;base64,{b(lat)});unicode-range:U+0000-00FF,U+2013-2014,U+00AB,U+00BB}}"
            f"@font-face{{font-family:{fam};src:url(data:font/woff2;base64,{b(cyr)});unicode-range:U+0400-04FF}}")
CSS = (face('T', 'alumni-sans/files/alumni-sans-latin-900-normal.woff2', 'alumni-sans/files/alumni-sans-cyrillic-900-normal.woff2')
       + "html,body{margin:0;background:transparent}.c{width:1080px;height:1920px;position:relative;color:#E8E2D6}")
logo = base64.b64encode(pathlib.Path('/home/claude/repo/docs/icon.png').read_bytes()).decode()
OUT = pathlib.Path('/home/claude/inc/out'); OUT.mkdir(exist_ok=True)

SCENE_TOP, SCENE_H = 640, 600
HOOK_BOTTOM = 1920 - SCENE_TOP + 20   # hook block ends 20px above scene

def page(html):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{html}</body></html>'

with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page(viewport={'width': 1080, 'height': 1920})
    for k, c in CLIPS.items():
        h1, h2 = c['hook']; size = 118
        while True:
            html = f'''<div class=c>
<div style="position:absolute;left:64px;right:64px;bottom:{HOOK_BOTTOM}px"><div id=h style="font-family:T;font-size:{size}px;line-height:.92;text-transform:uppercase;letter-spacing:1px;white-space:nowrap;display:inline-block">{h1}<br>{h2}</div>
<div style="margin:26px 0 0 -12px;width:560px;height:7px;background:#C1121F;transform:rotate(-1deg)"></div></div>
<img src="data:image/png;base64,{logo}" style="position:absolute;right:64px;bottom:250px;width:120px;height:120px;opacity:.55;border-radius:10px"></div>'''
            pg.set_content(page(html)); pg.wait_for_timeout(300)
            w = pg.evaluate("document.getElementById('h').getBoundingClientRect().width")
            if w <= 952 or size <= 70: break
            size -= 4
        pg.screenshot(path=str(OUT / f'ov{k}.png'), omit_background=True)
        print(k, 'hook size', size)
    pg.set_content(page(f'<div class=c style="background:#0B0B0C;display:flex;align-items:center;justify-content:center"><img src="data:image/png;base64,{logo}" style="width:560px;height:560px"></div>'))
    pg.wait_for_timeout(300); pg.screenshot(path=str(OUT / 'end.png'))
    br.close()

# ASS subtitles
t = open('/mnt/user-data/uploads/Incantation_2022_1080p_NF__WEB-DL_DUAL__DDP5__1_x264-SMURF-en.srt', encoding='utf-8-sig').read()
bl = re.findall(r'(\d\d):(\d\d):(\d\d),(\d+) --> (\d\d):(\d\d):(\d\d),(\d+)\n', t)
sec = lambda h, m, x, ms: int(h) * 3600 + int(m) * 60 + int(x) + int(ms) / 1000
cues = [(sec(*q[:4]), sec(*q[4:])) for q in bl]
fmt = lambda v: f"{int(v//3600)}:{int(v%3600//60):02d}:{v%60:05.2f}"
head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: S,Alumni Sans Thin Black,78,&H00D6E2E8,&H00D6E2E8,&H000C0B0B,&H00000000,0,0,0,0,100,100,1,0,1,3,0,8,64,64,{SCENE_TOP+SCENE_H+28},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
for k, c in CLIPS.items():
    lines = []; base = 0
    for a, z in c['p']:
        for s0, e0 in cues:
            key = round(s0, 2)
            if key in RU and RU[key] and e0 > a and s0 < z:
                st = max(s0, a) - a + base; en = min(e0 + .15, z) - a + base
                lines.append(f"Dialogue: 0,{fmt(st)},{fmt(en)},S,,0,0,0,,{RU[key]}")
        base += z - a
    (OUT / f'sub{k}.ass').write_text(head + '\n'.join(lines) + '\n', encoding='utf-8')
    missing = [round(s0, 2) for s0, e0 in cues for a, z in c['p'] if e0 > a and s0 < z and round(s0, 2) not in RU]
    print(k, len(lines), 'subs', 'MISSING' if missing else '', missing)
