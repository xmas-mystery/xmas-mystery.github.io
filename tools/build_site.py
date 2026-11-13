"""Baut die Website: verschluesselt die Tagesinhalte und schreibt sie ins Repository.

Klartext-Inhalte liegen in build/content/day-XX.json und werden NIE ins Repo kopiert.
Fehlt eine Datei, wird ein Platzhalter verschluesselt.
"""
import base64, hashlib, json, os, secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

REPO = "/home/claude/xmas-mystery.github.io"
BUILD = "/home/claude/build"
SALT = b"xmas-mystery-2026"
ITER = 150000

tokens = json.load(open("/home/claude/private/tokens.json"))
preview = open("/home/claude/private/preview.txt").read().strip()


def b64(b):
    return base64.b64encode(b).decode()


def norm(s):
    s = s.lower().strip()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        s = s.replace(a, b)
    return "".join(ch for ch in s if ch.isascii() and ch.isalnum())


os.makedirs(f"{REPO}/d", exist_ok=True)
for f in os.listdir(f"{REPO}/d"):
    os.remove(f"{REPO}/d/{f}")

for day_s, token in tokens.items():
    day = int(day_s)
    path = f"{BUILD}/content/day-{day:02d}.json"
    if os.path.exists(path):
        content = json.load(open(path))
    else:
        content = {"title": f"Tag {day}",
                   "story": "<p>Die Akte für diesen Tag wird noch geschrieben.</p>"}
    content["day"] = day
    # Klartext-Antworten in Hashes umwandeln, damit sie nicht lesbar mitgeliefert werden
    chk = content.get("check")
    if chk and "plain_answers" in chk:
        chk["answers"] = [hashlib.sha256(norm(a).encode()).hexdigest() for a in chk.pop("plain_answers")]

    key = hashlib.pbkdf2_hmac("sha256", token.encode(), SALT, ITER, dklen=32)
    iv = secrets.token_bytes(12)
    ct = AESGCM(key).encrypt(iv, json.dumps(content, ensure_ascii=False).encode(), None)
    rec = {"unlock": f"2026-12-{day:02d}", "iv": b64(iv), "ct": b64(ct)}
    fid = hashlib.sha256(token.encode()).hexdigest()[:20]
    json.dump(rec, open(f"{REPO}/d/{fid}.json", "w"))

page = open(f"{BUILD}/template.html").read().replace(
    "__PREVIEW_HASH__", hashlib.sha256(preview.encode()).hexdigest())
for name in ("index.html", "404.html"):
    open(f"{REPO}/{name}", "w").write(page)
open(f"{REPO}/.nojekyll", "w").write("")
open(f"{REPO}/robots.txt", "w").write("User-agent: *\nDisallow: /\n")
print("gebaut:", len(tokens), "Akten")
