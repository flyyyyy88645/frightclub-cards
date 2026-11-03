# Коннекторы: инструменты и рейтинги

> Справочник скилла horror-news-digest. Правила работы — только в скилле; здесь — данные и код. Правится коммитом без карточки скилла.
> Читать, когда нужен конкретный инструмент коннектора, его параметры или диагностика; про переменные и cron — worker.md.

## frightclubtg (основной)
Свой MCP-сервер Тимура на Cloudflare Workers: `frightclub-tg.flyyyyy92.workers.dev`, версия 1.11.1 от 3.11.2026. Код и переменные — worker.md.

- **TMDB:** `tmdb_search` / `tmdb_details` (режиссёр, даты релиза РФ и США, трейлер, `festivals` — фестивальные показы из TMDB), `tmdb_list` (upcoming, now_playing, discover по жанру 27), `tmdb_images` + `tmdb_view_image` (постеры и кадры; файл попадает в tool-results).
- **Рейтинги:** `movie_ratings` (Rotten Tomatoes критики, Metacritic, IMDb — из OMDb). Примеры, почему только по `tmdb_id`/`imdb_id`: по названию+году цеплялись одноимённые (The Void 2016, The Lodge, короткометражка The Ritual) или «Movie not found» (Tiger Stripes, Deerskin); RT не отдавался из-за расхождения года — «Пустота» на RT заведена как 2017.
- **Новости:** `horror_news` (RSS: Bloody Disgusting, Dread Central, iHorror, /Film Horror, Horror Society; параметры `hours`, `query`, `sources`) — быстрее и дешевле веб-поиска для «что нового». `news_week` — архив всего, что воркер видел в лентах, до 11 дней (для обзора за неделю; по умолчанию 30 новостей, `limit` до 200, `ru: true` — пересказ по-русски, `refresh: true` — сначала перечитать ленты). `horror_digest` — подборка (ручной запуск — worker.md).
- **YouTube:** `youtube_search` (`hours`, `order=viewCount`, `shorts`), `youtube_comments` (ключ задан 31.10.2026), `youtube_transcript` — текст видео из субтитров без ключа, длинное частями через `offset` = `next_offset` (порция по умолчанию 8000 символов с 1.11.0; если нужно всё видео целиком — просить `max_chars` до 60000); некоторые видео YouTube закрывает для Cloudflare проверкой «не бот» — тогда Тимур присылает «Показать текст видео».
- **Internet Archive:** `archive_search` (хорроры из коллекции feature_films) → `archive_item` (прямые ссылки на mp4 по размеру и на субтитры; поле `license`).
- **Reddit:** в воркере нет (заявку отклонили 1.11.2026; код удалён в 1.11.1 — worker.md).
- **Архив отправленного:** `digest_history` (подборки и новости, точный текст, 30 дней; `full: false` — кратко).
- **Агент:** `agent_setup` / `agent_ask` (worker.md).
- **TikTok:** `tiktok_auth`, `tiktok_upload`, `tiktok_status` (tiktok.md).
- **Telegram:** `tg_send_photo`, `tg_send_message`, `tg_send_album` (2–10 фото/видео, подпись на первом), `tg_send_poll`, `tg_edit_message`, `tg_delete_message`, `tg_pin_message`, `tg_get_updates` (с 1.6.0 отдаёт числовой `chat_id`), `tg_get_chat`, `tg_view_photo`.
  - **Куда уходит без `chat_id` (с 1.11.0):** `tg_send_*` — в личку Тимура (`PREVIEW_CHAT_ID`, если задан, иначе `DIGEST_CHAT_ID` = 249823375), **не в канал**. В канал — только явным `chat_id: "@frightclub88"`. `tg_edit_message`, `tg_delete_message`, `tg_pin_message` без `chat_id` возвращают ошибку — адрес обязателен. `tg_get_chat` без `chat_id` — по-прежнему канал (`DEFAULT_CHAT_ID`, только чтение). До 1.11.0 всё без `chat_id` уходило в канал.
- **Диагностика:** `server_status` — версия, env_present, tools_visible; `check: true` — пробные запросы ко второму боту, Gemini, YouTube.

## Другие коннекторы
- **frightclub** (Yandex Cloud) — Авито; Telegram оттуда недоступен (блокировка api.telegram.org из РФ). У него были свои `tg_*` с теми же именами, что у frightclubtg; 3.11.2026 Тимур отключил этот коннектор в Claude.
- **AnythingMCP** — был временным, пробный период до 31.10.2026; 3.11.2026 отключён в Claude. Принимает те же photo file_id, что frightclubtg (проверено 27.10).

## Рейтинги: почему OMDb
Официального открытого API у Rotten Tomatoes нет (только бизнес-лицензия / Fabric). Зрительского рейтинга в OMDb нет; Popcornmeter — лишь через неофициальные парсеры (API.market ~$0.001 за запрос, RapidAPI, Apify). Решение 31.10.2026: остаёмся на OMDb.
