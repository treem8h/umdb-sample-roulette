#!/bin/bash
# Cron notturno: rigenera videos.json (discovery yt-dlp gratis + validazione YouTube API) + push su GitHub
set -uo pipefail
cd /home/francesco/miliardo-beats/06_ROULETTE || exit 1
# lock anti-overlap: se un run precedente e' ancora in corso, esci senza pasticci
exec 9>tools/.refresh.lock
flock -n 9 || { echo "=== $(date '+%Y-%m-%d %H:%M') refresh gia' in corso, skip ===" >> tools/refresh.log; exit 0; }
LOG=/home/francesco/miliardo-beats/06_ROULETTE/tools/refresh.log
echo "=== $(date '+%Y-%m-%d %H:%M') refresh pool ===" >> "$LOG"
/home/francesco/miliardo-beats/01_ANALYTICS/api_privati/venv/bin/python tools/build_pool_api.py >> "$LOG" 2>&1
# versiona il nuovo pool
if ! git diff --quiet videos.json 2>/dev/null; then
  git add videos.json
  git -c user.email="unmiliardodibeats@gmail.com" -c user.name="Un Miliardo di Beats" commit -q -m "pool refresh $(date +%Y-%m-%d)" 2>>"$LOG"
  git push -q origin master 2>>"$LOG" && echo "  pushed" >> "$LOG"
fi
echo "  pool ora: $(python3 -c "import json;print(len(json.load(open('videos.json'))))" 2>/dev/null) video" >> "$LOG"
