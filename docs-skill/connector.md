# Коннекторы: инструменты и рейтинги

> Справочник скилла horror-news-digest. Правила работы — только в скилле; здесь — данные и код. Правится коммитом без карточки скилла.
> Читать, когда нужен конкретный инструмент коннектора, его параметры или диагностика; про переменные и cron — worker.md.

## frightclubtg (основной)
Свой MCP-сервер Тимура на Cloudflare Workers: `frightclub-tg.flyyyyy92.workers.dev`, версия 1.10.0 от 2.11.2026. Код и переменные — worker.md.

- **TMDB:** `tmdb_search` / `tmdb_details` (режиссёр, даты релиза РФ и США, трейлер, `festivals` — фестивальные показы из TMDB), `tmdb_list` (upcoming, now_playing, discover по жанру 27), `tmdb_images` + `tmdb_view_image` (постеры и кадры; файл попадает в tool-results).
- **Рейтинги:** `movie_ratings` (Rotten Tomatoes критики, Metacritic, IMDb — из OMDb).
- **Новости:** `horror_news` (RSS: Bloody Disgusting, Dread Central, iHorror, /Film Horror, Horror Society; параметры `hours`, `query`, `sources`) — быстрее и дешевле веб-поиска для «что нового». `horror_digest` — подборка (ручной запуск — worker.md).
- **YouTube:** `youtube_search` (`hours`, `order=viewCount`, `shorts`), `youtube_comments` (ключ задан 31.10.2026), `youtube_transcript` — текст видео из субтитров без ключа, длинное частями через `offset`; некоторые видео YouTube закрывает для Cloudflare проверкой «не бот» — тогда Тимур присылает «Показать текст видео».
- **Internet Archive:** `archive_search` (хорроры из коллекции feature_films) → `archive_item` (прямые ссылки на mp4 по размеру и на субтитры; поле `license`).
- **Reddit:** `reddit_top` (top/hot/new/rising/controversial, несколько сабов через `+`, `after`, `min_score`), `reddit_search`, `reddit_post` (полный текст + топ-комментарии) — появятся после одобрения заявки (worker.md).
- **Архив отправленного:** `digest_history` (подборки и новости, точный текст, 30 дней; `full: false` — кратко).
- **Агент:** `agent_setup` / `agent_ask` (worker.md).
- **TikTok:** `tiktok_auth`, `tiktok_upload`, `tiktok_status` (tiktok.md).
- **Telegram:** `tg_send_photo`, `tg_send_message`, `tg_send_album` (2–10 фото/видео, подпись на первом), `tg_send_poll`, `tg_edit_message`, `tg_delete_message`, `tg_pin_message`, `tg_get_updates` (с 1.6.0 отдаёт числовой `chat_id`), `tg_get_chat`, `tg_view_photo`.
- **Диагностика:** `server_status` — версия, env_present, tools_visible; `check: true` — пробные запросы ко второму боту, Gemini, YouTube.

## Другие коннекторы
- **frightclub** (Yandex Cloud) — Авито; Telegram оттуда недоступен (блокировка api.telegram.org из РФ).
- **AnythingMCP** — был временным, пробный период до 31.10.2026. Принимает те же photo file_id, что frightclubtg (проверено 27.10).

## Рейтинги: почему OMDb
Официального открытого API у Rotten Tomatoes нет (только бизнес-лицензия / Fabric). Зрительского рейтинга в OMDb нет; Popcornmeter — лишь через неофициальные парсеры (API.market ~$0.001 за запрос, RapidAPI, Apify). Решение 31.10.2026: остаёмся на OMDb.
