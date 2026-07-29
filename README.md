# 🎛️ UMDB Sample Roulette

A vintage-MPC-style **sample roulette** for beatmakers.
Hit **RANDOM** → it pulls a sampleable track from a curated pool → jump to a random spot → mark cut points on the 16 pads and chop.

Part of the **Un Miliardo di Beats** project.

## Features
- 🎲 Random sampleable track (curated pool, no API key needed)
- 🎹 16 MPC-style pads: tap to save a timestamp, tap again to jump (sample start)
- ⏱️ Jog buttons ±0.5 / 1 / 3 / 5 / 10s + clickable timeline for precise cueing
- ▶️ Play/Pause · Restart · pads work from keyboard (`1234 QWER ASDF ZXCV`)
- 💾 Pads saved in your browser (localStorage)

## Run locally
Any static server, e.g.:
```
python3 -m http.server 8899
```
then open http://localhost:8899

## Regenerate the sample pool
```
bash tools/build_pool.sh   # rebuilds videos.json via yt-dlp (no API key)
```

## Credits
Font: [Saira Semi Condensed](https://github.com/google/fonts/tree/main/ofl/sairasemicondensed) (OFL). Logo © Un Miliardo di Beats.
