"""Карточка «почему страшно» — шаблон по «пустому кадру» (31.10.2026), утверждён 7.11.2026.
python3 tools/why_card.py <кадр.jpg> "<ТЕМА>" "<номер части или ''>" cards/<YYYY-MM-DD-why-...>
Раскладка: вверху FRIGHTCLUB / РАЗБОР; широкий кадр 972×418 (top 292, left 54, наклон −0.8°);
«ПОЧЕМУ СТРАШНО» 170px с надрезом (top 950); тема красным 95.5px (top 1110); номер — тоже красным, тем же кеглем.
Без рейтинга и без подписи «кадр: …».
Крупный кадр (как «звук 1»): 6-й аргумент "top:120px;left:56px;width:968px;height:760px", pos "55% 50%".
7-й аргумент — подпись мелко под темой, откуда кадр: "кадр: логово дьявола · the haunting · 1963"."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
import card as C
def html(img, topic, num='', pos='50% 45%', box='top:120px;left:56px;width:968px;height:800px', sub=''):
    """Раскладка как у остальных обложек (card.py): кадр сверху от 120px, блок текста прижат к низу (bottom 64px),
    подпись «кадр: …» — 18px под темой. Кегли — как у «пустого кадра» 31.10."""
    data, _ = C.treat(img)
    T = "font-family:T;line-height:.85;text-transform:uppercase;white-space:pre"
    n = (f'<span style="{T};font-size:95.5px;color:#C1121F;margin-left:26px;display:inline-block">{num}</span>') if num else ''
    s = (f'<div style="margin-top:18px;font-size:19px;letter-spacing:3px;text-transform:uppercase;color:#8E8A82">{sub}</div>') if sub else ''
    return (f'<div class="card"><div class="mark"><b>frightclub</b><span>разбор</span></div>'
        f'<div style="position:absolute;{box};transform:rotate(-.8deg);box-shadow:0 30px 60px rgba(0,0,0,.6),0 0 0 1px #2a2a2c">'
        f'<img src="data:image/jpeg;base64,{data}" style="width:100%;height:100%;display:block;object-fit:cover;object-position:{pos}"></div>'
        f'<div style="position:absolute;left:58px;right:56px;bottom:64px">{C.sliced("ПОЧЕМУ СТРАШНО", 170, 54)}'
        f'<div style="display:flex;align-items:flex-end;margin-top:22px"><span style="{T};font-size:95.5px;color:#C1121F">{topic}</span>{n}</div>{s}</div></div>')

if __name__ == '__main__':
    C.ensure_fonts()
    img, topic, num, out = sys.argv[1:5]; pos = sys.argv[5] if len(sys.argv) > 5 else '50% 45%'
    kw = {'box': sys.argv[6]} if len(sys.argv) > 6 and sys.argv[6] else {}
    if len(sys.argv) > 7: kw['sub'] = sys.argv[7]
    C.render_many([(html(img, topic, num, pos, **kw), out)]); print(out + '.jpg')
