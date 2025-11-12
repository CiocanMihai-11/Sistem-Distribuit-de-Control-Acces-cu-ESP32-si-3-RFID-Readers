# AccesCriptat.py
# FastAPI + SQLite + AES-GCM (PyCryptodome) + HMAC-SHA256 (pepper)
# /enroll   -> inroleaza utilizatorul (cripteaza numele, salveaza in DB)
# /verify   -> verifica accesul dupa rfid_uid (prin cred_id derivat)
# /peek/... -> (doar pt test/admin) decripteaza numele
# /health   -> verificare simpla ca serverul e ok

import os, hmac, hashlib, base64, sqlite3
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, constr
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

app = FastAPI(title="AccesCriptat", version="1.0.0")

# ----------------------- UTIL: chei, normalizare, crypto -----------------------

def app_base_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))

def load_or_create(path: str, nbytes: int) -> bytes:
    """Creeaza fisierul de cheie daca nu exista, altfel il citeste."""
    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write(get_random_bytes(nbytes))
        # permisiuni restrictive unde sunt suportate (nu conteaza pe Windows)
        try:
            os.chmod(path, 0o600)
        except Exception:
            pass
    with open(path, "rb") as f:
        return f.read()

BASE = app_base_dir()
AES_KEY   = load_or_create(os.path.join(BASE, "aes.key"),    32)  # AES-256 pt. PII
PEPPER    = load_or_create(os.path.join(BASE, "pepper.key"), 32)  # HMAC pentru cred_id

def norm_uid(s: str) -> str:
    """Scoate spatiile si trece la uppercase, pt. consistenta."""
    return "".join(s.split()).upper()

def cred_id_from_uid(uid_str: str) -> str:
    """Deriveaza un ID determinist (dar nereversibil) din uid, cu HMAC-SHA256."""
    uid_n = norm_uid(uid_str)
    mac = hmac.new(PEPPER, uid_n.encode("utf-8"), hashlib.sha256).hexdigest()
    return mac  # 64 hex chars

def enc_field(plaintext: str) -> str:
    """AES-256-GCM: intoarce Base64(nonce(12) || tag(16) || ciphertext)."""
    nonce = get_random_bytes(12)                         # IV recomandat GCM
    c = AES.new(AES_KEY, AES.MODE_GCM, nonce=nonce)
    ct, tag = c.encrypt_and_digest(plaintext.encode("utf-8"))
    return base64.b64encode(nonce + tag + ct).decode("utf-8")

def dec_field(sealed_b64: str) -> str:
    """Inverseaza enc_field: Base64 -> bytes -> decriptare si verificare tag."""
    raw = base64.b64decode(sealed_b64)
    nonce, tag, ct = raw[:12], raw[12:28], raw[28:]
    c = AES.new(AES_KEY, AES.MODE_GCM, nonce=nonce)
    pt = c.decrypt_and_verify(ct, tag)
    return pt.decode("utf-8")

# ------------------------------ DB: SQLite -------------------------------------

DB_PATH = os.path.join(BASE, "acces.db")
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()
# setari pentru robustete
cur.execute("PRAGMA journal_mode=WAL;")
cur.execute("PRAGMA synchronous=NORMAL;")
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
  cred_id TEXT PRIMARY KEY,       -- HMAC-SHA256(pepper, norm_uid)
  encrypted_name TEXT NOT NULL,   -- nume criptat AES-GCM (Base64)
  enabled INTEGER NOT NULL,       -- 1 = activ, 0 = dezactivat
  rfid_uid_enc TEXT               -- OPTIONAL: uid brut criptat pentru audit
)
""")
conn.commit()

# --------------------------------- Schemas -------------------------------------

HexUID = constr(strip_whitespace=True, min_length=4, max_length=64, regex=r"^[0-9a-fA-F\s]+$")

class EnrollReq(BaseModel):
    name: str
    rfid_uid: HexUID
    enabled: bool = True

class VerifyReq(BaseModel):
    rfid_uid: HexUID

# -------------------------------- Endpoints ------------------------------------

@app.get("/health")
def health():
    return {"ok": True, "db": os.path.basename(DB_PATH)}

@app.post("/enroll", status_code=status.HTTP_201_CREATED)
def enroll_user(req: EnrollReq):
    """
    Inrolare utilizator:
    - deriveaza cred_id din rfid_uid (HMAC-SHA256)
    - cripteaza numele cu AES-GCM
    - salveaza in DB; REPLACE = upsert pe cheia primara (cred_id)
    """
    cid = cred_id_from_uid(req.rfid_uid)
    enc_name = enc_field(req.name)
    uid_enc = enc_field(norm_uid(req.rfid_uid))  # optional pt. audit; nu e folosit la decizie

    cur.execute(
        "REPLACE INTO users (cred_id, encrypted_name, enabled, rfid_uid_enc) VALUES (?, ?, ?, ?)",
        (cid, enc_name, int(req.enabled), uid_enc)
    )
    conn.commit()
    # nu intoarcem PII in raspuns (nici macar criptat) in productie; pt demo e ok sa omitem
    return {"cred_id": cid, "enabled": req.enabled}

@app.post("/verify")
def verify_access(req: VerifyReq):
    """
    Verifica accesul DOAR dupa cred_id (derivat din UID), fara decriptari.
    - 404 daca credentialul nu exista
    - 403 daca e dezactivat
    - 200 + access:true daca e activ
    """
    cid = cred_id_from_uid(req.rfid_uid)
    cur.execute("SELECT enabled FROM users WHERE cred_id = ?", (cid,))
    row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential inexistent")
    if row[0] == 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Dezactivat")
    return {"access": True}

@app.get("/peek/{rfid_uid}")
def peek_name(rfid_uid: str):
    """
    DOAR pentru test / admin (nu lasa endpointul expus in productie).
    Decripteaza numele stocat pentru un rfid_uid dat.
    """
    cid = cred_id_from_uid(rfid_uid)
    cur.execute("SELECT encrypted_name FROM users WHERE cred_id = ?", (cid,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Nu exista")
    name = dec_field(row[0])
    return {"rfid_uid_norm": norm_uid(rfid_uid), "name": name}
