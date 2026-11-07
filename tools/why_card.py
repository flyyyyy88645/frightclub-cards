"""Карточка «почему страшно» — шаблон по «пустому кадру» (31.10.2026), утверждён 7.11.2026.
python3 tools/why_card.py <кадр.jpg> "<ТЕМА>" "<номер части или ''>" cards/<YYYY-MM-DD-why-...>
Раскладка: вверху FRIGHTCLUB / РАЗБОР; широкий кадр 972×418 (top 292, left 54, наклон −0.8°);
«ПОЧЕМУ СТРАШНО» 170px с надрезом (top 950); тема красным 95.5px (top 1110); номер — светлая плашка с наклоном.
Без рейтинга и без подписи «кадр: …»."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).parent))
import card as C
def html(img, topic, num='', pos='50% 45%'):
    data, _ = C.treat(img)
    T = "font-family:T;line-height:.85;text-transform:uppercase;white-space:pre"
    n = (f'<span style="{T};font-size:95.5px;color:#0B0B0C;background:#E8E2D6;padding:4px 16px 0;margin-left:18px;'
         f'transform:rotate(-3deg);display:inline-block">{num}</span>') if num else ''
    return (f'<div class="card"><div class="mark"><b>frightclub</b><span>разбор</span></div>'
        f'<div style="position:absolute;top:292px;left:54px;width:972px;height:418px;transform:rotate(-.8deg);box-shadow:0 30px 60px rgba(0,0,0,.6),0 0 0 1px #2a2a2c">'
        f'<img src="data:image/jpeg;base64,{data}" style="width:100%;height:100%;display:block;object-fit:cover;object-position:{pos}"></div>'
        f'<div style="position:absolute;left:58px;top:950px">{C.sliced("ПОЧЕМУ СТРАШНО", 170, 54)}</div>'
        f'<div style="position:absolute;left:58px;top:1110px;display:flex;align-items:flex-end"><span style="{T};font-size:95.5px;color:#C1121F">{topic}</span>{n}</div></div>')
if __name__ == '__main__':
    C.ensure_fonts()
    img, topic, num, out = sys.argv[1:5]; pos = sys.argv[5] if len(sys.argv) > 5 else '50% 45%'
    C.render_many([(html(img, topic, num, pos), out)]); print(out + '.jpg')
