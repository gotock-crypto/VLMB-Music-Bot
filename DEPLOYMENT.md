# VLMB Music Bot — безопасное обновление production

Цель этой процедуры — обновить код **без перезаписи SQLite/Redis данных** и с быстрым rollback.

## 0. Перед первым запуском

На сервере должны существовать:

- `/root/MusBot/.env` — секреты;
- `/root/MusBot/venv/` — виртуальное окружение;
- `musicbot.service` — systemd unit;
- `bot_stats.db` и `vk_tokens.db` — production БД.

Содержимое `.env` должно быть примерно таким:

```env
TELEGRAM_BOT_TOKEN=НОВЫЙ_ТОКЕН_ОТ_BOTFATHER
YANDEX_TOKEN=ВАШ_YANDEX_TOKEN
VK_TOKEN=
LASTFM_API_KEY=ВАШ_LASTFM_API_KEY
REDIS_URL=redis://localhost:6379/0
INSTANCE_LOCK_FILE=
```

Права:

```bash
chmod 600 /root/MusBot/.env
chown root:root /root/MusBot/.env
```

**Важно:** старый Telegram token из серверного snapshot следует отозвать и выпустить новый.

## 1. Проверить release и сделать backup

Новый deployment сначала проверяет release и `.env`, пока текущий бот продолжает работать. Затем автоматически делает backup. Вручную останавливать сервис перед запуском `deploy_release.sh` не нужно.

```bash
cd /root/vlmb_release/MusBot
/root/MusBot/venv/bin/python3 scripts/preflight.py --env-file /root/MusBot/.env
```

После успешного preflight deployment-скрипт сам создаст backup:

```text
/root/MusBot-backup-YYYYMMDD-HHMMSS.tar.gz
```

После backup можно проверить его наличие:

```bash
ls -lh /root/MusBot-backup-*.tar.gz | tail -1
```

## 2. Распаковать новый архив во временный каталог

Не распаковывайте архив поверх production сразу.

```bash
mkdir -p /root/vlmb_release
tar -xzf /root/VLMB-Music-Bot-release.tar.gz -C /root/vlmb_release
```

Если архив содержит верхний каталог `MusBot`, дальше используйте `/root/vlmb_release/MusBot`.

## 3. Проверить код до переключения

```bash
cd /root/vlmb_release/MusBot
/root/MusBot/venv/bin/python3 scripts/preflight.py --env-file /root/MusBot/.env
/root/MusBot/venv/bin/python3 -m py_compile music_bot_user_mixes.py config.py services/*.py scripts/*.py
```

Если preflight сообщает отсутствие обязательного секрета — сначала заполните `/root/MusBot/.env`.

## 4. Обновить код, не трогая данные

```bash
cd /root
rsync -a --delete \
  --exclude='.env' \
  --exclude='bot_stats.db' \
  --exclude='bot_stats.db-shm' \
  --exclude='bot_stats.db-wal' \
  --exclude='vk_tokens.db' \
  --exclude='bot.log' \
  --exclude='bot-debug.log' \
  --exclude='venv/' \
  /root/vlmb_release/MusBot/ /root/MusBot/
```

Это критически важно: production БД и `.env` остаются на месте.

## 5. Обновить systemd unit

```bash
cp /root/MusBot/systemd/vlmb-musicbot.service /etc/systemd/system/musicbot.service
systemctl daemon-reload
```

## 6. Проверить окружение и БД

```bash
cd /root/MusBot
/root/MusBot/venv/bin/python3 scripts/preflight.py
/root/MusBot/venv/bin/python3 scripts/healthcheck.py
```

Ожидается `PASS` для обязательных проверок. Предупреждения по Redis/необязательным провайдерам допустимы только если вы сознательно их отключили.

## 7. Запуск

```bash
systemctl enable musicbot
systemctl restart musicbot
systemctl status musicbot --no-pager -l
```

Логи:

```bash
journalctl -u musicbot -n 100 --no-pager
tail -n 100 /root/MusBot/bot-debug.log
```

## 8. Monitoring

The 3.0.0 deployment installs `vlmb-healthcheck.service` and `vlmb-healthcheck.timer` automatically. Verify:

```bash
systemctl status vlmb-healthcheck.timer --no-pager
systemctl list-timers --all | grep vlmb-healthcheck
```

## 9. Smoke test

Проверить в Telegram:

1. `/start`
2. поиск простого трека;
3. скачивание VK/Yandex;
4. поиск/скачивание YouTube;
5. повторное скачивание уже отправленного трека;
6. `/history`;
7. `/mix`;
8. `/digest` в тестовой группе, если используется.

Проверить на сервере:

```bash
systemctl is-active musicbot
pgrep -af music_bot_user_mixes.py
```

Должен быть **ровно один** процесс бота. В старом snapshot встречались Telegram `409 Conflict`, что является признаком двух polling-клиентов одновременно. Новый instance lock + systemd restart должны исключать это.

## 10. Rollback

Если smoke test не проходит, используйте штатный rollback. Он **не удаляет production `venv`, `.env` и БД**, потому что backup намеренно не содержит эти объекты.

```bash
/root/MusBot/scripts/rollback_release.sh /root/MusBot-backup-YYYYMMDD-HHMMSS.tar.gz
```

Не восстанавливайте старые `.env`/credentials без необходимости.
