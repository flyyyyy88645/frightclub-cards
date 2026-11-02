# Нарезки: команды, оверлей, рендер, субтитры

> Справочник скилла horror-news-digest. Правила работы — только в скилле; здесь — данные и код. Правится коммитом без карточки скилла.
> Читать перед любой нарезкой (правила — скилл, раздел 7). Готовый конвейер пачкой — tools/clips/ (см. README там).

## Сверка тайминга файла и .srt
- SDH: 1–2 громких пика RMS против тегов [screams]/[crashing]. Совпало ±2 с — работаем; нет — считаем сдвиг.
- Не SDH (Netflix WEB-DL): корреляция «маска реплик × RMS» со сдвигом ±8 с; пик корреляции = сдвиг.
- Дорожки без меток языка (`und`): оригинальная обычно лучше коррелирует с таймингом srt, дубляж хуже.

## Поиск моментов
- Субтитры: парсить `.srt` → теги звуков (без шума вроде [leaves rustling], [sighs]) + паузы в репликах ≥35 с.
- Звук: RMS дБ по секундам в окне: `ffmpeg -ss S -t L -i film -vn -ac 1 -ar 8000 -f s16le -` → numpy. Пик = скачок >15 дБ после тишины.
- Склейки: `ffmpeg -ss S -t L -i film -an -vf "scale=320:-1,scdet=threshold=10" -f null -` → `lavfi.scd.time`.
- Лист на окно-кандидат 6×5: `fps=1/N,scale=200:-1,drawtext` с таймкодом, `tile=6x5` — видно сцену и где резать.
- Проверка пачки: один лист-раскадровка из кадров середины всех роликов по 200 px; полный осмотр — только при новом шаблоне.

## Параметры шаблона (1080×1920, 30 fps, H.264 + AAC)
- Фон: эта же сцена на весь кадр, boxblur 30, brightness −0.32 (светлый/белый кадр — −0.62), saturation 0.6.
- Центр (−20 px): сцена шириной 1080, saturation 0.8, contrast 1.06.
- Хук: Alumni Sans 900 капсом 118 px (длинные строки меньше, white-space:nowrap — ровно 2 строки), #E8E2D6; под ним в потоке красная линия #C1121F 560×7, −1°.
- Логотип FC справа внизу 120 px, opacity 0.55 (файл `docs/icon.png`).
- Зерно `noise=alls=7` (в тёмных 360p можно слабее); вспышка 0.1 с `drawbox=...:color=0xC1121F@0.45:t=fill:enable='between(t,T,T+0.1)'`; финал 1.4 с — логотип 560 px на #0B0B0C, fade-in 0.25 с, звук затухает 0.5 с.
- Тихая сцена: громкость участка +10…18 дБ с лимитером; шум — `afftdn`.

## Оверлей
Оверлей (`ov.py`, Playwright, прозрачный PNG; аргументы: хук1 хук2 → overlay.png + end.png):
```python
# CSS/шрифты — как в docs-skill/cards.md (face('T',...), face('M',...)), плюс html,body{background:transparent}; .c{width:1080px;height:1920px;position:relative;color:#E8E2D6;font-family:M}
over=f'''<div class=c>
<div style="position:absolute;left:64px;right:64px;bottom:1250px"><div style="font-family:T;font-size:118px;line-height:.92;text-transform:uppercase;letter-spacing:1px">{hook1}<br>{hook2}</div>
<div style="margin:26px 0 0 -12px;width:560px;height:7px;background:#C1121F;transform:rotate(-1deg)"></div></div>
<img src="data:image/png;base64,{logo}" style="position:absolute;right:64px;bottom:250px;width:120px;height:120px;opacity:.55;border-radius:10px"></div>'''
end=f'''<div class=c style="background:#0B0B0C;display:flex;flex-direction:column;align-items:center;justify-content:center">
<img src="data:image/png;base64,{logo}" style="width:560px;height:560px"></div>'''
# pg.screenshot(path=..., omit_background=True) для обоих, viewport 1080×1920
```

Рендер одного куска (S, D = старт и длина в с, R = время вспышки от начала ролика, E=1.4):
```bash
ffmpeg -v error -y -ss $S -t $D -i "$F" -loop 1 -i overlay.png -loop 1 -i end.png -filter_complex \
"[0:v]fps=30,setsar=1,split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:3,eq=brightness=-0.32:saturation=0.6[bg];\
[b]scale=1080:-2,eq=saturation=0.8:contrast=1.06[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2-20[o1];\
[o1][1:v]overlay=0:0:shortest=1,subtitles=sub.ass:fontsdir=/home/claude/fontdl/ttf,noise=alls=7:allf=t,\
drawbox=x=0:y=0:w=iw:h=ih:color=0xC1121F@0.45:t=fill:enable='between(t,$R,$R+0.1)',tpad=stop_mode=clone:stop_duration=$E[v2];\
[2:v]format=rgba,fade=in:st=0:d=0.25:alpha=1,setpts=PTS+$D/TB[endc];[v2][endc]overlay=0:0:enable='gte(t,$D)',format=yuv420p[v];\
[0:a]afade=t=in:d=0.3,afade=t=out:st=$(echo "$D-0.5"|bc):d=0.5,apad=pad_dur=$E[aout]" \
-map "[v]" -map "[aout]" -t $(echo "$D+$E"|bc) -c:v libx264 -crf 22 -preset veryfast -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart out.mp4
```
Два куска — два `-ss/-t` входа, `concat=n=2:v=1:a=1` перед split. Рендер ~1 мин на ролик.

## Субтитры (ASS)
- Шрифт: Alumni Sans 900 из npm (woff2) → TTF: fontTools (`pip install fonttools brotli --break-system-packages`), сохранить latin и cyrillic woff2 как ttf (`flavor=None`) и слить `fontTools.merge.Merger` в `/home/claude/fontdl/ttf/AlumniSans-Black.ttf` (временные файлы убрать). Имя семейства в ASS: `Alumni Sans Thin Black`.
- Стиль: `PlayResX 1080, PlayResY 1920, WrapStyle 2`; `Style: S,Alumni Sans Thin Black,78,&H00D6E2E8,&H00D6E2E8,&H000C0B0B,&H00000000,0,0,0,0,100,100,1,0,1,3,0,8,64,64,1200,1` (верх-центр, y=1200 — сразу под сценой). Конец реплики +0.15 с; длинные — `\N` на 2 строки.
