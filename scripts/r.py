import requests, secrets, sys
B="http://10.0.173.208:5000"
s=requests.Session(); s.headers["User-Agent"]="Mozilla/5.0"
u="t"+secrets.token_hex(4); p="Passw0rd!123"
r=s.post(f"{B}/signup",data={"username":u,"password":p},timeout=20,allow_redirects=False)
print("signup:",r.status_code,r.headers.get("Location"))
r=s.get(f"{B}/",timeout=20); print("home:",r.status_code,len(r.text))
r=s.get(f"{B}/account/drafts",timeout=20); print("drafts:",r.status_code,len(r.text))
import re
print("draft rows:",re.findall(r'href="/([^"/]+)/(?:unlock|preview)"',r.text)[:10])
# home listings
r=s.get(f"{B}/",timeout=20)
print("listing ids:",sorted(set(re.findall(r'/listings/(\d+)',r.text)))[:20])
open("home.html","w").write(r.text)
