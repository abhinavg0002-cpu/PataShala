import hashlib
import hmac
import secrets
import time

ITER = 120_000
_fails = {}          # code -> (count, locked_until). shortcut: in memory, resets on restart; fine for one school server.
MAX_FAILS, LOCK_S = 5, 60


def hash_pin(pin, salt=None):
    salt = salt or secrets.token_hex(8)
    h = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt.encode(), ITER).hex()
    return h, salt


def check_pin(pin, h, salt):
    return hmac.compare_digest(hash_pin(pin, salt)[0], h)


def new_token():
    t = secrets.token_urlsafe(32)
    return t, hashlib.sha256(t.encode()).hexdigest()


def token_hash(t):
    return hashlib.sha256(t.encode()).hexdigest()


def locked(code):
    c, until = _fails.get(code, (0, 0))
    return until > time.time()


def fail(code):
    c, until = _fails.get(code, (0, 0))
    c += 1
    _fails[code] = (c, time.time() + LOCK_S if c >= MAX_FAILS else 0)
    if c >= MAX_FAILS:
        _fails[code] = (0, time.time() + LOCK_S)


def ok(code):
    _fails.pop(code, None)
