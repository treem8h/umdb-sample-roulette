#!/bin/bash
# Genera il pool di video campionabili (videos.json) — algoritmo di selezione UMDB Roulette
# Nessuna API key: usa yt-dlp search. Rigenera/espandi quando vuoi.
YT=/home/francesco/.local/bin/yt-dlp
OUT=/home/francesco/miliardo-beats/06_ROULETTE/videos.json
TMP=$(mktemp)

# query mirate a musica CAMPIONABILE (strumentale/vinile/groove globali)
QUERIES=(
  "funk instrumental 45" "soul instrumental" "rare groove funk" "library music"
  "jazz funk fusion" "vinyl rip soul" "70s funk break" "brazilian funk"
  "bossa nova instrumental" "ethiopian jazz" "turkish psych funk" "afrobeat instrumental"
  "disco instrumental" "gospel funk" "breakbeat drums" "italian library music"
  "french library music" "spanish funk" "psychedelic soul" "lofi jazz vinyl"
  "rhodes soul instrumental" "obscure funk 45" "jazz drum breaks" "dusty soul sample"
  "cinematic library funk"
)

for q in "${QUERIES[@]}"; do
  $YT --flat-playlist --no-warnings \
    --print "%(id)s|%(duration)s|%(title)s" "ytsearch20:$q" 2>/dev/null >> "$TMP"
  echo "  ok: $q ($(wc -l < "$TMP") righe totali)"
done

# filtra durata 45-720s, dedup per id, costruisci JSON
python3 - "$TMP" "$OUT" << 'PY'
import sys,json
seen={}
for ln in open(sys.argv[1]):
    p=ln.rstrip("\n").split("|",2)
    if len(p)<3: continue
    vid,dur,title=p
    try: d=int(float(dur))
    except: continue
    if not vid or vid in seen: continue
    if d<45 or d>720: continue            # canzoni, non clip né mix lunghissimi
    seen[vid]={"id":vid,"d":d,"t":title[:80]}
pool=list(seen.values())
json.dump(pool, open(sys.argv[2],"w"), ensure_ascii=False)
print(f"POOL: {len(pool)} video campionabili -> {sys.argv[2]}")
PY
rm -f "$TMP"
