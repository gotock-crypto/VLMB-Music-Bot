# Обновление VLMB Music Bot до 4.0.0-rc1

> Важно: 3.0.6 остаётся рабочей production-точкой. RC1 — архитектурный релиз. Перед заливкой обязательно сделать backup и не удалять его до полного Telegram smoke-test.

## 1. Windows PowerShell

Архив после сборки:

```powershell
scp "D:\1\Инет\VLMB-Music-Bot-release-2026-08-22-v4.0.0-rc1.tar.gz" root@45.43.90.131:/root/VLMB-release.tar.gz
ssh root@45.43.90.131
```

## 2. Проверить production до обновления

```bash
systemctl status musicbot --no-pager
systemctl is-active musicbot
pgrep -fc music_bot_user_mixes.py
```

Должно быть `active` и ровно `1` процесс.

## 3. Распаковать RC

```bash
rm -rf /root/vlmb_release
mkdir -p /root/vlmb_release
tar -xzf /root/VLMB-release.tar.gz -C /root/vlmb_release
```

Проверить структуру:

```bash
find /root/vlmb_release -maxdepth 2 -type f | sort | head -80
```

Если архив имеет верхний каталог `VLMB-Music-Bot`, использовать:

```bash
mv /root/vlmb_release/VLMB-Music-Bot /root/vlmb_release/MusBot
```

Иначе оставить содержимое непосредственно в `/root/vlmb_release/MusBot` согласно `RELEASE_DIR`.

## 4. Рекомендуемый deployment

```bash
export RELEASE_DIR=/root/vlmb_release/MusBot
bash "$RELEASE_DIR/scripts/deploy_release.sh"
```

Скрипт теперь делает backup **до** изменения production venv/dependencies.

Он также выполняет:

```text
preflight
compile
backup
install dependencies
cutover
healthcheck
start
process count
healthcheck
```

При ошибке после начала cutover выполняется rollback.

## 5. Проверка после deploy

```bash
systemctl status musicbot --no-pager -l
systemctl is-active musicbot
pgrep -fc music_bot_user_mixes.py
/root/MusBot/venv/bin/python3 /root/MusBot/scripts/preflight.py --env-file /root/MusBot/.env
/root/MusBot/venv/bin/python3 /root/MusBot/scripts/healthcheck.py
```

## 6. Проверить новый architecture layer

```bash
cd /root/MusBot
python3 scripts/callback_audit.py
python3 scripts/architecture_audit.py
python3 scripts/load_test_queue.py --jobs 100 --concurrency 10 --work-ms 20
python3 scripts/rollback_drill.py
```

## 7. Telegram smoke-test

Обязательно пройти:

```text
/start
→ поиск
→ результат
→ скачать
→ добавить в избранное
→ убрать из избранного
→ история
→ повторная загрузка
→ Похожие
→ поиск исполнителя
→ Назад
→ новое меню
```

Дополнительно проверить:

```text
charts
settings
help
pagination
more
playlist/album
```

Особенно внимательно проверить `Похожие → поиск → назад`, потому что этот flow ранее ломался.

## 8. Если RC1 сломан

Сразу:

```bash
systemctl status musicbot --no-pager -l
journalctl -u musicbot -n 200 --no-pager
ls -lht /root/MusBot-backup-*.tar.gz | head
```

Не удалять backup.

Если deployment script уже выполнил rollback — повторно ничего не распаковывать до анализа логов.

Для ручного rollback использовать существующий production rollback script с конкретным backup:

```bash
bash /root/MusBot/scripts/rollback_release.sh /root/MusBot-backup-YYYYMMDD-HHMMSS.tar.gz
systemctl daemon-reload
systemctl restart musicbot
systemctl status musicbot --no-pager -l
```

## 9. После успешной проверки

Сохранить backup минимум до следующего релиза.

Проверить Git SHA и release version:

```bash
cd /root/MusBot
git rev-parse HEAD 2>/dev/null || true
cat RELEASE_VERSION
```

Ожидается:

```text
4.0.0-rc1
```

## 10. Реальный rollback drill (обязательно перед production acceptance)

Это отдельная проверка, которая намеренно ломает deployment **после cutover** и должна заставить `deploy_release.sh` восстановить backup.

Сначала убедиться, что 3.0.6 backup уже создан обычным deployment/upgrade flow. Затем подготовить RC1 как обычно и выполнить:

```bash
export RELEASE_DIR=/root/vlmb_release/MusBot
FORCE_FAIL_AFTER_CUTOVER=1 bash "$RELEASE_DIR/scripts/deploy_release.sh"
```

Ожидаемый результат:

```text
Deployment failed ... restoring previous release...
```

После завершения проверить:

```bash
systemctl is-active musicbot
pgrep -fc music_bot_user_mixes.py
cat /root/MusBot/RELEASE_VERSION
```

Должно быть:

```text
active
1
3.0.6
```

И затем:

```bash
/root/MusBot/venv/bin/python3 /root/MusBot/scripts/healthcheck.py
```

должен вернуть:

```text
Healthcheck OK
```

**Важно:** `FORCE_FAIL_AFTER_CUTOVER=1` используется только для этого drill. В обычном deployment его не задавать.
