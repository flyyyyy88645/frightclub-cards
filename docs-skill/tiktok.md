# TikTok и Instagram: устройство, лимиты, аудит

> Справочник скилла horror-news-digest. Правила работы — только в скилле; здесь — данные и код. Правится коммитом без карточки скилла.
> Читать перед загрузкой роликов в TikTok, при ошибках загрузки и когда Тимур возвращается к аудиту или Instagram.

## Как устроено
- Приложение «frightclub» в TikTok for Developers (владелец — организация Тимура), режим **Sandbox**, тестовый аккаунт (Target user) — TikTok-аккаунт **frightclub**. Разрешения: `user.info.basic`, `video.upload`.
- Ролики уходят во «Входящие» аккаунта (черновик); прямой постинг (`video.publish`) — только после аудита.
- Инструменты коннектора frightclubtg: `tiktok_auth` (ссылка живёт 15 мин: войти аккаунтом frightclub → Authorize → чёрная страница «tiktok подключён»; доступ обновляется сам, refresh — на год), `tiktok_upload` (`video_url` → `publish_id`), `tiktok_status` (без аргументов — `connected`; с `publish_id` — статус).
- Статусы: PROCESSING_UPLOAD — TikTok обрабатывает (бывает несколько минут) → SEND_TO_USER_INBOX — доставлено; FAILED — смотреть `fail_reason`.
- Где Тимур находит ролик: в телефоне, аккаунт frightclub → Входящие → системные уведомления → открыть видео → вставить подпись → опубликовать. В веб-версии уведомления не видны. Подпись загрузка не переносит.
- Доступ к TikTok и метки хранятся в KV `TIKTOK_KV` воркера (см. worker.md).

## Лимиты
- Файл ≤64 МБ уходит одним куском, до 120 МБ — частями (воркер режет сам), больше — пережать.
- GitHub не принимает файлы >100 МБ.
- Бот Telegram не берёт по ссылке файлы >20 МБ — лёгкие копии 720×1280 в `clips/tg/`.
- Во «Входящих» не больше ~5 неопубликованных (`spam_risk_too_many_pending_share`); после серии отказов — rate limit.
- `mode: "pull"` (TikTok скачивает сам) работает только с подтверждённого адреса github.io.

## Аудит (план — когда нужно 3–4 ролика в день)
Записать демо-видео всего процесса (вход → загрузка → публикация из приложения), заполнить App review в Production, отправить. После одобрения: Production Client Key → переменная `TIKTOK_CLIENT_KEY`, Production Client Secret → `TIKTOK_CLIENT_SECRET`, заново `tiktok_auth`; при желании добавить `video.publish` (Direct Post) и инструмент прямой публикации.

## Instagram (не построено)
Свой MCP: Instagram API with Instagram Login, Graph API — контейнер REELS по публичному `video_url` → ожидание FINISHED → `media_publish`; видео по raw-ссылке GitHub/R2. До готовности Тимур выкладывает вручную.
