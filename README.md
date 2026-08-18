# 🎵 VLMB Music Bot

**Асинхронный Telegram-бот для поиска и скачивания музыки** из трёх популярных источников: **Яндекс.Музыка**, **VK** и **YouTube**.

Бот разработан с использованием AI-ассистентов (Cursor, Claude Code) и ориентирован на высокую нагрузку: 500+ активных пользователей, 1000+ запросов в день, среднее время ответа < 2 секунды, uptime 99.9%.

---

## 🚀 Возможности

- 🔍 Поиск музыки по названию трека или исполнителю.
- 🎵 Интеграция с API Яндекс.Музыки, VK Audio и YouTube (yt-dlp).
- ⚡ Асинхронная архитектура (asyncio, aiohttp) для высокой производительности.
- 🧠 Кеширование результатов через Redis + LRU-кеш.
- 📦 Умная маршрутизация: приоритет точного совпадения с исполнителем.
- 🎧 Скачивание и отправка аудиофайлов в Telegram.
- 🛡️ Автоматические ретраи с backoff, ротация токенов VK.
- 📊 Встроенная админ-панель для управления токенами и настройками.
- 🎲 Подборки по жанрам (Deezer) и поиск похожих исполнителей (Last.fm).
- 💾 Кеширование Telegram `file_id` для мгновенной отправки ранее загруженных треков.

---

## 🛠️ Стек технологий

| Компонент | Технология |
|-----------|------------|
| Язык | Python 3.12+ |
| Фреймворк | python-telegram-bot (асинхронный) |
| Веб-фреймворк | aiohttp |
| Кеширование | Redis + LRU-кеш в памяти |
| База данных | SQLite (aiosqlite) |
| Музыкальные API | Yandex Music, VK API, YouTube (yt-dlp) |
| Администрирование | systemd, Ubuntu VPS, Docker |
| AI-инструменты | ChatGPT, Claude, Cursor |

---

## 📦 Установка и запуск

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/gotock-crypto/VLMB-Music-Bot.git
cd VLMB-Music-Bot
```

### 2. Создайте виртуальное окружение
```bash
python3 -m venv venv
source venv/bin/activate  # Для Linux/macOS
venv\Scripts\activate     # Для Windows
```

### 3. Установите зависимости
```bash
pip install -r requirements.txt
```

### 4. Настройте переменные окружения
Создайте файл `.env` на основе примера:
```bash
cp .env.example .env
```
Заполните в `.env` свои токены:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
YANDEX_TOKEN=your_yandex_token
VK_TOKEN=your_vk_token
LASTFM_API_KEY=your_lastfm_api_key
REDIS_URL=redis://localhost:6379/0
```

### 5. Запустите бота
```bash
python music_bot_user_mixes.py
```

---

## 🌐 Деплой на сервер

Для продакшена рекомендуется использовать **systemd** для автозапуска и перезапуска.

Пример файла `/etc/systemd/system/musicbot.service`:
```ini
[Unit]
Description=VLMB Music Bot
After=network.target

[Service]
User=root
WorkingDirectory=/root/MusBot
ExecStart=/root/MusBot/venv/bin/python3 /root/MusBot/music_bot_user_mixes.py
Restart=always
RestartSec=10
EnvironmentFile=/root/MusBot/.env

[Install]
WantedBy=multi-user.target
```

Затем выполните:
```bash
systemctl enable musicbot
systemctl start musicbot
```

---

## 🧠 Архитектура проекта

```text
MusBot/
├── music_bot_user_mixes.py   # Основной код бота
├── config.py                  # Конфигурация (токены, настройки)
├── bot_stats.db               # SQLite база данных (создаётся автоматически)
├── vk_tokens.db               # Хранилище VK токенов
├── requirements.txt           # Зависимости Python
├── .env.example               # Шаблон для переменных окружения
└── README.md                  # Этот файл
```

**Ключевые модули:**
- `YandexMusicManager` — работа с API Яндекс.Музыки.
- `YoutubeMusicManager` — загрузка аудио через yt-dlp.
- `AsyncVKTokenManager` — управление и ротация токенов VK.
- `AsyncCacheManager` — кеширование через Redis + локальный LRU.
- `AsyncSessionManager` — управление сессиями поиска пользователей.
- `AdminDB` — админ-панель для статистики, банов, рассылок.
- `UserStore` — хранение истории и предпочтений пользователей.

---

## 🔒 Безопасность

- Все токены хранятся в `.env` и **не** попадают в репозиторий.
- Для VK реализована ротация токенов и автоматическое обновление.
- Настроена фильтрация секретов в логах.
- Поддерживается бан пользователей через админ-панель.

---

## 📈 Мониторинг и надежность

- **Uptime:** 99.9% (подтверждено на production).
- **MTTR:** < 5 минут (автоматический перезапуск через systemd).
- **Логирование:** ротация логов, мониторинг состояния через `journalctl`.
- **Кеширование:** Redis + локальный LRU-кеш для снижения нагрузки на API.

---

## 🤝 Вклад и развитие

Проект активно развивается. Для предложений и баг-репортов создавайте Issues или Pull Requests.

---

## 📝 Лицензия

MIT License

---

## ✉️ Контакты
**GitHub:** [gotock-crypto](https://github.com/gotock-crypto)