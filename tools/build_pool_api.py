#!/usr/bin/env python3
"""Genera videos.json (pool sample campionabili) via YouTube Data API.
Filtri: categoria MUSICA (10) + embeddable + syndicated + durata 45-600s + no mix/karaoke/live.
Nessuna key esposta al client: il pool risultante è statico. Rigenera per espandere/rinnovare."""
import json, re, time, os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

HERE=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(HERE,"..","videos.json")
TOKEN="/home/francesco/miliardo-beats/01_ANALYTICS/api_privati/token.json"
creds=Credentials.from_authorized_user_file(TOKEN)
yt=build('youtube','v3',credentials=creds)

QUERIES=[
 "funk instrumental","soul instrumental","jazz funk","boogie funk","disco instrumental",
 "rare groove","library music","breakbeat","psych rock instrumental","garage rock",
 "bossa nova","samba funk","afrobeat","highlife","ethio jazz","turkish funk",
 "italian library music","french library music","krautrock","spanish funk","gospel funk",
 "rhythm and blues instrumental","northern soul","jazz fusion","rhodes soul","moog funk",
 "cinematic soundtrack instrumental","giallo soundtrack","lounge exotica","latin jazz",
 "salsa dura","cumbia","tropicalia","reggae instrumental","dub instrumental",
 "soul 45","funk 45","jazz drums break","vintage soul","70s funk","60s soul",
 "brazilian groove","japanese city pop","korean funk","nigerian funk","peruvian cumbia",
 "sitar funk","hammond organ jazz","blaxploitation soundtrack","spy jazz"
]
ORDERS=["relevance","viewCount","rating","date"]
BAD=re.compile(r'(\btype beat\b|typebeat|\bfree\b|prod\.|prod by|no copyright|copyright free|'
               r'\b1 hour\b|\b2 hour\b|\b3 hour\b|full album|\bmix\b|nonstop|non-stop|karaoke|tutorial|'
               r'how to|reaction|live at|live in|lyrics?|documentary|interview|top \d|best of|'
               r'compilation|playlist|mixtape|dj set|full ep|full lp|megamix|continuous|sped up|slowed)', re.I)

def iso_to_sec(s):
    m=re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?',s or '')
    if not m: return 0
    h,mi,se=(int(x) if x else 0 for x in m.groups()); return h*3600+mi*60+se

pool={}; calls=0
# MERGE: parti dal pool esistente (cresce nel tempo invece di ripartire da zero)
if os.path.exists(OUT):
    try:
        for v in json.load(open(OUT)):
            if v.get('id'): pool[v['id']]=v
        print(f"  pool esistente: {len(pool)} video (aggiungo i nuovi)")
    except: pass
for qi,q in enumerate(QUERIES):
    order=ORDERS[qi%len(ORDERS)]
    token=None
    for page in range(2):                      # 2 pagine per query = fino a 100 risultati
        try:
            r=yt.search().list(part='snippet',q=q,type='video',videoCategoryId='10',
                videoEmbeddable='true',videoSyndicated='true',maxResults=50,
                order=order,pageToken=token,relevanceLanguage='en').execute()
            calls+=1
        except Exception as e:
            print(f"  search err '{q}': {str(e)[:70]}"); break
        ids=[it['id']['videoId'] for it in r.get('items',[]) if it.get('id',{}).get('videoId')]
        titles={it['id']['videoId']:it['snippet']['title'] for it in r.get('items',[]) if it.get('id',{}).get('videoId')}
        # durata + status via videos.list (batch 50)
        if ids:
            try:
                v=yt.videos().list(part='contentDetails,status,statistics',id=','.join(ids)).execute(); calls+=1
                for it in v.get('items',[]):
                    vid=it['id']; d=iso_to_sec(it['contentDetails']['duration'])
                    st=it.get('status',{})
                    views=int(it.get('statistics',{}).get('viewCount',0) or 0)
                    if d<45 or d>600: continue
                    if not st.get('embeddable',True): continue
                    if views>300000: continue          # niente hit famose → roba da digger (poche views)
                    t=titles.get(vid,'')
                    if BAD.search(t): continue
                    if vid in pool: continue
                    pool[vid]={"id":vid,"d":d,"t":t[:80],"v":views}
            except Exception as e:
                print(f"  videos err: {str(e)[:60]}")
        token=r.get('nextPageToken')
        if not token: break
    print(f"  [{qi+1}/{len(QUERIES)}] {q:28} pool={len(pool)}")
    time.sleep(0.2)

arr=list(pool.values())
json.dump(arr, open(OUT,"w"), ensure_ascii=False)
print(f"\n✅ POOL: {len(arr)} sample puliti (musica, embeddable, 45-600s) | {calls} chiamate API")
print(f"   -> {os.path.abspath(OUT)}")
