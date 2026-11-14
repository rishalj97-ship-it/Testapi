import base64, getpass, gzip, json, queue, re, socket, ssl, struct, threading, time
import urllib.parse, urllib.request, os
from flask import Flask, request, jsonify
from datetime import datetime
import random 

# ------------------------------------------------------------------ config ----
STATIC_KEY = b"Yg&tc%DEuh6%Zc^8"
STATIC_IV  = b"6oyZDr22E3ychjM%"
CLIENT_SECRET = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
APP_ID = "100067"
OAUTH_URL = "https://100067.connect.garena.com/oauth/guest/token/grant"
MAJOR_LOGIN_URL = "https://loginbp.ppmainecoonghj.com/MajorLogin"
DEFAULT_CLIENT_HOST = "https://client.ind.freefiremobile.com"
CLIENT_VERSION, RELEASE_VERSION, REGION = "2.133.11", "OB55", "IND"

AUTH_OPCODES = (0x93, 0x95, 0x89, 0x7B, 0x69, 0x8F, 0x78, 0x83)
ONLINE_OPCODES = (0x8D, 0x86, 0x67) + AUTH_OPCODES
REGION_BYTE = {"BD": 0x19, "IND": 0x14}

# emotes fired after every successful join
EMOTE_LIST = [
    909000098, 909000098, 909000098, 909000098, 909000098,
    909000001, 909000001, 909000001, 909000001, 909000001
]


TARGET_UID = 6112290940

BOT_UID = os.getenv("BOT_UID", "").strip()
BOT_PASSWORD = os.getenv("BOT_PASSWORD", "").strip()
EMOTE_GAP = 4.0


TEMPLATE_UID, TEMPLATE_CODE = b"18827556186", b"9809812"   # from capture seq 39
JOIN_TEMPLATE_B64 = (
    "CAQSzwoiCAEJChIZICcpKgc5ODA5ODEyMAZAAUq5CQoZSU5ESUFfTk9USU5JVD8xODgyNzU1NjE4NhAXGvcDd19ZUBQDCEQEAg4I"
    "U1YNB1ABWwMCWQJUVwQOVgAIU1ddAA9TAlMLABsAB0R0W0VBThoIFAAfGwAESQVRfHoLXm5Ja3l/Z05Eem5ff3wHcA1gfABxdQwV"
    "CU1jBV9hVV5oZ1J/BG9vB39EcU1+A0x3XWRWdH8FG1dZVkUZZn0adUhIA0pgXHB9Yl1jTmBYZlRZVwVUUVoPUX4DCXkCA3wKEQkL"
    "TVFcVll9V2Zac2gHHVNmUUMNA2Rgc35ES3pacAgUCkRMBmYXWmVnGm0LfEtrXEtaRHxeThl2E15OS3ALFgdLaHx2AWdqYlcAZH9r"
    "am9QYktERAF0AEJTS1BBBRIPSX1eQmJfY2ZIRldNYw9HDl0CAAB6XH14XlZQXwwVCQlKckdAe05hQ3J9WlQAZ3N5anx/d09iemUa"
    "WXpPBRIFRF9/e08HHUJ/Vn5Td2J9c0RweghCWHoJeVABVA8bDE1bSEl8TFNBfmB1eFBQUmxvY0RUam12BklTWlIIFAAIRFJsQGMG"
    "TGVNXXQXYWxaYH13YWBDXXBiT0AAbwgWAk5gVnpkSnAGVwx6dloTf3hNfExgBhxnanxaVwgMFQJJZlluSX0ZAXB7UQMcClZ8WXd9"
    "f0VPQm9QAE5aCxsHSnsMeVhZXGJ8aEFEAG1HeQ4AclAMcHENeW5lAAUiBHldVl0wDjoKEnB2YG9zZ2QcHEIIMi4xMzMuMTJIAlAC"
    "Wv0EA2JiU1E2ekhJMkFzSUFkVjJLeW9WbGRtZ201L3lmUE1Hd09oMmlnekdJd0xKKzRxb2JJZU1ybkxOUm1xU1kxcjh3Nm5Lb3M2"
    "Y1lqcEk0RWVUVnE2YWhLcUttN1hEVEc4UlFIWjNvOWpBMzFKbXZyRFFncmZXb3Z4YU5VbU9CNXF6UTlGZ0tGbEtqRS9hd25oOXhQ"
    "cTdqVUlxMVUxTHpreWIydXV1QXYzemRQYkxpbUQva1FwMVMxNEpjbmdyd2NtQUtvWmE0ZHpJOFkyanZ3ZTJ3QWVLbERxMU5VWSsx"
    "WDVhcXY3Unl1bDIzVVR0eUkzajBhbEI3NC91SkhGUC83NFhncVFHRHhzcDRJeUIxUWFDcWZ1M3I0VVdheUlMd1BXMGJjZC9sQkF4"
    "Um43RUg5aXhBUTdleEdVdWdHVzBVZ0NrMHBXenAvNWNWZVB0cTRybzlWRmNHN1VWbVlTY1oxZm1lWjdvUHIrNXpuemlSS1V5bUR1"
    "L1JhNHMyY2VUczVaKzFzZ1RwVXAwZk5mNXV5dzBDd1VzeTdsVTdzTGtVZWJ3NThjeGtSYkNVUUFTVWVudGk4NGNyazVhdks4aXVS"
    "elFsbVpNb3VSb1M4ZGhxWFo2NU1FTDlyVzFTWmFtMEVxNnRFajYxMHgxSEFjUzlVUlVLUG15OHg1QWc3Z2pqVnpIQU1DbWtUVXda"
    "TTVlYzFaazRFZ2lPd3dBbFhOeDFncGpoZW4zWlhCeTlYSFQyOXI0SkJlc3VYWlA0cEJlSkkwRjB3NGduRUFMaFZsZll2ekRiY3NO"
    "S3pRSVhvWjk4S0ZsYW01a1pTUlhiN0RkZ1NOVFhsV2xWWER3enFrPVoNCgRJREMxED0aA0lORFoNCgRJREMyEBEaA0lORGoCZW6C"
    "AQQ3T1IZogEFCAMQ+QKiAQUIBBCHA6IBBQgFEJ8BogEFCB0QyAGiAQQIFhBcogEFCA4QkAGiAQIIFboBFWFfNTg2OTU0NjgyNDM0"
    "MTM4Mzk3N9oBBAgCEAQ="
)


try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    _AES_BACKEND = "pycryptodome"

    def aes_enc(data, key=STATIC_KEY, iv=STATIC_IV):
        return AES.new(key, AES.MODE_CBC, iv).encrypt(pad(data, 16))

    def aes_dec(data, key=STATIC_KEY, iv=STATIC_IV):
        return unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(data), 16)
except ImportError:
    from cryptography.hazmat.primitives import padding as _pd
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    _AES_BACKEND = "cryptography"

    def aes_enc(data, key=STATIC_KEY, iv=STATIC_IV):
        p = _pd.PKCS7(128).padder()
        c = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
        return c.update(p.update(data) + p.finalize()) + c.finalize()

    def aes_dec(data, key=STATIC_KEY, iv=STATIC_IV):
        c = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
        u = _pd.PKCS7(128).unpadder()
        return u.update(c.update(data) + c.finalize()) + u.finalize()


def aes_dec_raw(data, key=STATIC_KEY, iv=STATIC_IV):
    if not data or len(data) % 16 != 0:
        return None
    try:
        if _AES_BACKEND == "pycryptodome":
            return AES.new(key, AES.MODE_CBC, iv).decrypt(data)
        c = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
        return c.update(data) + c.finalize()
    except Exception:
        return None

# ---------------------------------------------------------------- protobuf ----
def _wv(n):
    out = bytearray()
    while True:
        b = n & 0x7F; n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b); return bytes(out)


def _rv(b, i):
    n = s = 0
    while True:
        c = b[i]; i += 1
        n |= (c & 0x7F) << s; s += 7
        if not c & 0x80:
            return n, i


def pb_parse(b):
    i, out = 0, []
    while i < len(b):
        k, i = _rv(b, i)
        f, w = k >> 3, k & 7
        if f == 0:
            raise ValueError("field 0")
        if w == 0:
            v, i = _rv(b, i)
        elif w == 2:
            l, i = _rv(b, i)
            if i + l > len(b):
                raise ValueError("overrun")
            v, i = b[i:i + l], i + l
        elif w == 1:
            v, i = b[i:i + 8], i + 8
        elif w == 5:
            v, i = b[i:i + 4], i + 4
        else:
            raise ValueError("wire type")
        out.append((f, w, v))
    return out


def pb_build(fields):
    out = bytearray()
    for f, w, v in fields:
        out += _wv(f << 3 | w)
        out += _wv(v) if w == 0 else (_wv(len(v)) + v if w == 2 else v)
    return bytes(out)


def pb_get(fields, n):
    for f, w, v in fields:
        if f == n:
            return v


def pb_encode(d):
    out = []
    for k, v in d.items():
        if isinstance(v, int):
            out.append((k, 0, v))
        else:
            out.append((k, 2, v.encode() if isinstance(v, str) else bytes(v)))
    return pb_build(out)


def retarget(b, repl, depth=0):
    if b and all(32 <= c < 127 for c in b):
        for old, new in repl.items():
            b = b.replace(old, new)
        return b
    try:
        fields = pb_parse(b)
        if depth < 8 and fields and pb_build(fields) == b:
            return pb_build([(f, w, retarget(v, repl, depth + 1) if w == 2 else v) for f, w, v in fields])
    except Exception:
        pass
    for old, new in repl.items():
        b = b.replace(old, new)
    return b

# --------------------------------------------------------------------- HTTP ----
def http_post(url, data, headers, verify=True, timeout=30):
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    ctx = None if verify else ssl._create_unverified_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.status, r.read()


# ----- validators (mirror MaJorLogin.py detection) -----
def _v_major_login(fields):
    nums = {f for f, w, v in fields}
    if 8 in nums:
        for f, w, v in fields:
            if f == 8 and w == 2:
                if isinstance(v, bytes):
                    try:
                        s = v.decode("utf-8", "ignore")
                        if s.count(".") == 2:
                            return True
                    except Exception:
                        pass
                elif isinstance(v, str) and v.count(".") == 2:
                    return True
        return False
    return 1 in nums and 21 in nums


def _v_login_data(fields):
    for f, w, v in fields:
        if f == 14 and w == 2 and isinstance(v, bytes):
            try:
                s = v.decode("utf-8", "ignore")
                return ":" in s and s.count(".") >= 1
            except Exception:
                return False
    return False


def parse_response(raw, validator):

    if raw[:2] == b"\x1f\x8b":
        try:
            raw = gzip.decompress(raw)
        except Exception:
            pass

    candidates = []
    try:
        candidates.append(("aes", aes_dec(raw, STATIC_KEY, STATIC_IV)))
    except Exception:
        d = aes_dec_raw(raw, STATIC_KEY, STATIC_IV)
        if d:
            candidates.append(("aes-raw", d))

    if len(raw) > 64:
        try:
            candidates.append(("aes@64", aes_dec(raw[64:], STATIC_KEY, STATIC_IV)))
        except Exception:
            d = aes_dec_raw(raw[64:], STATIC_KEY, STATIC_IV)
            if d:
                candidates.append(("aes-raw@64", d))
        candidates.append(("raw@64", raw[64:]))

    candidates.append(("raw", raw))

    for label, buf in candidates:
        if not buf:
            continue
        try:
            fields = pb_parse(buf)
        except Exception:
            continue
        if fields and validator(fields):
            return fields

    print("[debug] unparseable response: %d bytes" % len(raw))
    print("[debug] hex:", raw[:96].hex())
    try:
        print("[debug] text:", raw[:200].decode("utf-8", "ignore").replace("\n", " ")[:200])
    except Exception:
        pass
    raise ValueError("cannot parse server response")


def _s(fields, n, default=""):
    v = pb_get(fields, n)
    return v.decode(errors="ignore") if isinstance(v, bytes) else default

# -------------------------------------------------------------------- login ----
def oauth(uid, password, verify):
    body = urllib.parse.urlencode({"uid": uid, "password": password, "response_type": "token",
                                   "client_type": "2", "client_secret": CLIENT_SECRET,
                                   "client_id": APP_ID}).encode()
    st, raw = http_post(OAUTH_URL, body, {
        "User-Agent": "GarenaMSDK/4.0.19P9(SM-M526B ;Android 13;en;IN;)",
        "Content-Type": "application/x-www-form-urlencoded", "Connection": "close"}, verify, 20)
    j = json.loads(raw)
    if not j.get("open_id") or not j.get("access_token"):
        raise RuntimeError("OAuth failed: %s" % j)
    return j["open_id"], j["access_token"]


def _client_info(open_id, access_token, platform="4", extra=None):
    d = {3: datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 4: "free fire", 5: 1, 7: CLIENT_VERSION,
         8: "Android OS 10 / API-29 (QP1A.190711.020/1617006012)", 9: "Handheld", 10: "Vi India", 11: "WIFI",
         12: 1600, 13: 720, 14: "320", 15: "ARM64 FP ASIMD AES | 2301 | 8", 16: 2799,
         17: "PowerVR Rogue GE8320", 18: "OpenGL ES 3.2 build 1.11@5425693",
         19: "Google|9f7d6b8b-b10c-454a-852d-06332cd498eb", 20: "151.158.158.220", 21: "en",
         22: open_id, 23: platform, 24: "Handheld", 25: "realme RMX2189", 26: REGION,
         29: access_token, 30: 1, 41: "Vi India", 42: "WIFI", 57: "1ac4b80ecf0478a44203bf8fac6120f5",
         60: 19799, 61: 2536, 62: 5056, 64: 2768, 65: 19999, 66: 2536, 67: 19799, 73: 1,
         74: "/data/app/com.dts.freefiremax-ShI7E0dK8p1IiZ785pvuVQ==/lib/arm64", 76: 2,
         77: "38f4751a330688ab124c2c804cec90a5|/data/app/com.dts.freefiremax-ShI7E0dK8p1IiZ785pvuVQ==/base.apk",
         78: 2, 79: 2, 81: "64", 83: "2019118527", 86: "OpenGLES3", 87: 3071, 88: 4, 92: 67920,
         93: "android_max",
         94: "KqsHT+UrR1HKqb6+1db+Ofei+NtZr2+hbiBo3yKDL8w+8E3S5qF2IgEEe1fFQFyHRzl4iyHjHp+QsfeLbjJ6+DidTiKxm0ak2uYYa6QR4nAUdlZR",
         95: 111107, 96: '{"cur_rate":null,"support_etc2":true}', 97: 1, 98: 1, 99: platform, 100: platform,
         102: "", 104: 83812, 105: 1,
         106: "https://dl-bs.ggpolarbear.com/live/ABHotUpdates/|https://core-bs.ggpolarbear.com/live/ABHotUpdates/|a4332cb1c1a84e51dd77441e4856ed5a",
         107: "1.9393e7b8e53e8aeb"}
    d.update(extra or {})
    return pb_encode(d)


def _ga_headers(bearer=""):
    return {
        "User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
        "Accept": "*/*",
        "Accept-Encoding": "deflate, gzip",
        "X-GA-SV": str(int(time.time())),
        "Authorization": "Bearer " + bearer,
        "X-GA": "v1 1",
        "ReleaseVersion": RELEASE_VERSION,
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Unity-Version": "2018.4.12f1",
    }


# ----- friendly MajorLogin decode (field 1 is BOT account_id) -----
_ML_LABELS = {
    1: "account_id (BOT uid)",
    2: "region",
    3: "url",
    8: "JWT",
    10: "client_url",
    21: "server_time",
    22: "SESSION KEY",
    23: "SESSION IV",
}


def dump_major_login(fields):
    print("[major_login] decoded response (%d fields):" % len(fields))
    for f, w, v in fields:
        label = _ML_LABELS.get(f, "")
        pad = ("  [%s]" % label) if label else ""
        if w == 0:
            line = "  f%-3d varint = %-12s%s" % (f, v, pad)
        elif w == 2:
            if isinstance(v, bytes):
                if f in (22, 23) and len(v) == 16:
                    line = "  f%-3d len    = 0x%-32s (%d B)%s" % (f, v.hex(), len(v), pad)
                else:
                    try:
                        s = v.decode("utf-8")
                        s_short = s if len(s) <= 60 else (s[:56] + "…")
                        line = "  f%-3d len    = %r%s" % (f, s_short, pad)
                    except Exception:
                        line = "  f%-3d len    = 0x%s (%d B)%s" % (f, v.hex()[:32], len(v), pad)
            else:
                line = "  f%-3d len    = %r%s" % (f, v, pad)
        else:
            line = "  f%-3d w%d     = %r%s" % (f, w, v, pad)
        print(line)


def major_login(open_id, access_token, verify):

    st, raw = http_post(MAJOR_LOGIN_URL, aes_enc(_client_info(open_id, access_token)), _ga_headers(), verify)
    r = parse_response(raw, _v_major_login)

    dump_major_login(r)

    bot_uid = pb_get(r, 1)
    jwt = _s(r, 8)
    key = pb_get(r, 22)
    iv  = pb_get(r, 23)

    if not isinstance(bot_uid, int):
        raise RuntimeError("MajorLogin field 1 is not a varint account_id (got %r)" % (bot_uid,))
    if not isinstance(key, (bytes, bytearray)) or len(key) != 16:
        raise RuntimeError("MajorLogin field 22 is not a 16-byte KEY (got %r)" % (key,))
    if not isinstance(iv, (bytes, bytearray)) or len(iv) != 16:
        raise RuntimeError("MajorLogin field 23 is not a 16-byte IV (got %r)" % (iv,))
    if jwt.count(".") != 2:
        raise RuntimeError("MajorLogin field 8 is not a JWT")

    return {"jwt": jwt, "key": bytes(key), "iv": bytes(iv),
            "uid": bot_uid, "kts": pb_get(r, 21) or int(time.time()),
            "client_url": _s(r, 10) or DEFAULT_CLIENT_HOST}


def get_login_data(login, open_id, access_token, verify):
    body = aes_enc(_client_info(open_id, access_token, "4",
                                {20: "27.59.76.15", 90: "New Delhi", 91: "DL", 99: "0"}))
    st, raw = http_post(login["client_url"].rstrip("/") + "/GetLoginData",
                        body, _ga_headers(login["jwt"]), verify, 20)
    r = parse_response(raw, _v_login_data)
    online = _s(r, 14)
    if ":" not in online:
        raise RuntimeError("no online server in GetLoginData")
    return {"online": online, "chat": _s(r, 32), "region": _s(r, 3, REGION).upper()}

# ------------------------------------------------------------------ packets ----
def frame(ptype_hex, payload, key, iv):
    ct = aes_enc(payload, key, iv)
    return bytes.fromhex(ptype_hex) + struct.pack(">I", len(ct)) + ct


def build_auth(opcode, region, uid, kts, jwt, key, iv):
    enc = aes_enc(jwt.encode(), key, iv)
    return (bytes([opcode, REGION_BYTE.get(region.upper(), 0x15)]) + int(uid).to_bytes(8, "big")
            + int(kts).to_bytes(4, "big") + b"\x00\x00\x00\x00" + struct.pack(">I", len(enc)) + enc)


def build_heartbeat(key, iv):
    return frame("0e14", b"\x08\x20", key, iv)


def build_join(team_code, uid, key, iv):
    tpl = base64.b64decode("".join(JOIN_TEMPLATE_B64))
    return frame("0514", retarget(tpl, {TEMPLATE_UID: str(uid).encode(),
                                        TEMPLATE_CODE: str(team_code).encode()}), key, iv)


DEFAULT_EMOTE_ID = 909000001


DEFAULT_EMOTE_ID = 909000001

DEFAULT_EMOTE_ID = 909000001


def build_emote(my_uid, target_uid, emote_id, key, iv):
    inner = pb_build([
        (1, 0, int(my_uid)),
        (2, 0, DEFAULT_EMOTE_ID),
        (5, 2, pb_build([
            (1, 0, int(target_uid)),
            (3, 0, int(emote_id))
        ]))
    ])

    return frame("0514", pb_build([
        (1, 0, 21),
        (2, 2, inner)
    ]), key, iv)


def build_prime(target_uid, key, iv):
    a = frame("0514", pb_build([
        (1, 0, 72),
        (2, 2, pb_build([
            (1, 0, int(target_uid))
        ]))
    ]), key, iv)

    b = frame("0f14", pb_build([
        (1, 0, 1),
        (2, 2, pb_build([
            (1, 2, _wv(int(target_uid))),
            (2, 0, 13)
        ]))
    ]), key, iv)

    return a, b


def selftest():
    plain = pb_build([
        (1, 0, 21),
        (2, 2, pb_build([
            (1, 0, 18827556186),
            (2, 0, DEFAULT_EMOTE_ID),
            (5, 2, pb_build([
                (1, 0, 6112290940),
                (3, 0, DEFAULT_EMOTE_ID)
            ]))
        ]))
    ])

    assert plain.hex() == "0815121a08daead6914610c1fab8b1032a0c08fcd0c8e21618c1fab8b103", plain.hex()

    assert retarget(
        base64.b64decode(JOIN_TEMPLATE_B64),
        {
            TEMPLATE_UID: TEMPLATE_UID,
            TEMPLATE_CODE: TEMPLATE_CODE
        }
    ) == base64.b64decode(JOIN_TEMPLATE_B64)

    mine = pb_build([
        (1, 0, 21),
        (2, 2, pb_build([
            (1, 0, 19117544805),
            (2, 0, DEFAULT_EMOTE_ID),
            (5, 2, pb_build([
                (1, 0, TARGET_UID),
                (3, 0, DEFAULT_EMOTE_ID)
            ]))
        ]))
    ])

    assert mine.hex() == "0815121a08e5aafa9b4710c1fab8b1032a0c0898b5add73618c1fab8b103", mine.hex()

    k, i = bytes(range(16)), bytes(range(16, 32))

    original_list = EMOTE_LIST[:]

    try:
        EMOTE_LIST[:] = [DEFAULT_EMOTE_ID]

        pkt = build_emote(19117544805, TARGET_UID, DEFAULT_EMOTE_ID, k, i)

        assert pkt[:2] == bytes.fromhex("0514")
        assert struct.unpack(">I", pkt[2:6])[0] == len(pkt) - 6
        assert aes_dec(pkt[6:], k, i) == mine

    finally:
        EMOTE_LIST[:] = original_list

    prime_a, prime_b = build_prime(TARGET_UID, k, i)

    assert prime_a[:2] == bytes.fromhex("0514")
    assert prime_b[:2] == bytes.fromhex("0f14")

    return True

# -------------------------------------------------------------- connection ----
def recv_frame(sock, timeout):
    sock.settimeout(timeout)

    def need(n):
        buf = b""
        while len(buf) < n:
            c = sock.recv(n - len(buf))
            if not c:
                raise ConnectionError("closed")
            buf += c
        return buf
    try:
        h = need(5)
    except socket.timeout:
        return None
    return h[:1].hex(), need(struct.unpack(">I", h[1:])[0])


class Conn:
    def __init__(self, name, host, port, auth_packets, ping_packet, ping_every, on_frame):
        self.name, self.host, self.port = name, host, int(port)
        self.auth_packets, self.ping_packet, self.ping_every, self.on_frame = auth_packets, ping_packet, ping_every, on_frame
        self.lock, self.stop, self.sock = threading.Lock(), threading.Event(), None

    def connect(self):
        for opcode, pkt in self.auth_packets:
            s = socket.create_connection((self.host, self.port), timeout=15)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            print("[%s] connected %s:%s, auth opcode 0x%02x" % (self.name, self.host, self.port, opcode))
            s.sendall(pkt)
            try:
                first = recv_frame(s, 4.0)
            except (ConnectionError, OSError):
                first = None
            if first:
                self.sock, self.first = s, first
                print("[%s] auth reply: %s (%d bytes)" % (self.name, first[0], len(first[1])))
                return
            print("[%s] no reply / closed, trying next opcode" % self.name)
            s.close()
        raise RuntimeError("%s server never answered the auth packet" % self.name)

    def start(self):
        self.on_frame(self.name, *self.first)
        threading.Thread(target=self._reader, daemon=True).start()
        threading.Thread(target=self._pinger, daemon=True).start()

    def send(self, data):
        with self.lock:
            self.sock.sendall(data)

    def _reader(self):
        while not self.stop.is_set():
            try:
                f = recv_frame(self.sock, 1.0)
            except (ConnectionError, OSError):
                print("[%s] connection closed" % self.name)
                self.stop.set()
                return
            if f:
                self.on_frame(self.name, *f)

    def _pinger(self):
        while not self.stop.is_set():
            try:
                self.send(self.ping_packet)
            except OSError:
                self.stop.set()
                return
            self.stop.wait(self.ping_every)

    def close(self):
        self.stop.set()
        try:
            self.sock.close()
        except Exception:
            pass

# -------------------------------------------------------------------- bot ----
def team_reply(ptype, body, my_uid):
    if ptype != "05":
        return None
    try:
        top = pb_parse(body)
    except Exception:
        return None
    team = pb_get(top, 5)
    if isinstance(team, bytes):
        t = pb_parse(team)
        uids = [pb_get(t, 1)] + [pb_get(pb_parse(v), 1) for fn, w, v in t if fn == 6 and w == 2]
        return "joined", [u for u in uids if isinstance(u, int) and u != int(my_uid)]
    if pb_get(top, 3) is not None and pb_get(top, 2) == 5:
        return "failed", pb_get(top, 3)
    return None


class Bot:
    def __init__(self, lg):
        self.uid = int(lg["uid"])              # MajorLogin field 1
        self.key, self.iv = lg["key"], lg["iv"]
        self.verdicts = queue.Queue()
        self.online = None

    def on_frame(self, name, ptype, body):
        if name == "online":
            v = team_reply(ptype, body, self.uid)
            if v:
                self.verdicts.put(v)

    def join(self, code, wait=10.0):
        while not self.verdicts.empty():
            self.verdicts.get_nowait()
        self.online.send(build_join(code, self.uid, self.key, self.iv))
        print("[bot] join packet sent for team code", code)
        try:
            return self.verdicts.get(timeout=wait)
        except queue.Empty:
            return None

    def prime(self, target_uid):
        for p in build_prime(target_uid, self.key, self.iv):
            self.online.send(p)
        time.sleep(0.5)

    def emote(self, target_uid, emote_id):
        pkt = build_emote(self.uid, target_uid, emote_id, self.key, self.iv)
        self.online.send(pkt)

    def fire_emote_list(self, target_uid, gap=EMOTE_GAP):
        self.prime(target_uid)
        total = 0
        cycle = 0
        total_pkts = len(EMOTE_LIST)
        print("[bot] continuous emote cycle started; press Ctrl+C to stop")
        while True:
            cycle += 1
            print("[bot] cycle %d" % cycle)
            for idx, eid in enumerate(EMOTE_LIST, 1):
                self.emote(target_uid, eid)
                total += 1
                print("  [%2d/%2d] emote %-10s -> %-12s | sent: %d" %
                      (idx, total_pkts, eid, target_uid, total))
                time.sleep(gap)


# ---------------------------------------------------------------- Flask API ----
app = Flask(__name__)
_api_lock = threading.Lock()


def run_api_emote(team_code, emote_id, target_uid=None):
    """Login, join the requested team, send emote, then close TCP."""

    uid = BOT_UID.strip()
    password = BOT_PASSWORD.strip()

    if not uid or not password:
        raise RuntimeError("BOT_UID or BOT_PASSWORD is missing")

    bot = None

    try:
        print("[login] OAuth ...")
        open_id, access_token = oauth(uid, password, True)

        print("[login] MajorLogin ...")
        login = major_login(open_id, access_token, True)

        print("[login] GetLoginData ...")
        login_data = get_login_data(login, open_id, access_token, True)

        host, port = login_data["online"].rsplit(":", 1)
        region = login_data["region"]
        key, iv = login["key"], login["iv"]

        bot = Bot(login)
        bot.online = Conn(
            "online",
            host,
            int(port),
            [
                (
                    op,
                    build_auth(
                        op,
                        region,
                        login["uid"],
                        login["kts"],
                        login["jwt"],
                        key,
                        iv
                    )
                )
                for op in ONLINE_OPCODES
            ],
            build_heartbeat(key, iv),
            10.0,
            bot.on_frame
        )

        bot.online.connect()
        bot.online.start()

        print("[team] Joining team:", team_code)

        verdict = bot.join(team_code, wait=10.0)

        if verdict is None:
            raise RuntimeError("No team-join response received")

        if verdict[0] != "joined":
            raise RuntimeError("Team join refused: %s" % verdict[1])

        members = verdict[1]

        if target_uid is not None:
            targets = [int(target_uid)]
        else:
            targets = list(dict.fromkeys(int(x) for x in members))

        if not targets:
            raise RuntimeError(
                "No teammate UID returned; provide Target_Uid"
            )

        sent_to = []

        for uid_to_emote in targets:
            bot.emote(uid_to_emote, int(emote_id))
            sent_to.append(uid_to_emote)

        print(
            "[api] Emote sent successfully | Emote: %s | Sent To: %s"
            % (emote_id, sent_to)
        )

        time.sleep(4.0)

        return {
            "ok": True,
            "TeaM_Code": str(team_code),
            "EmoTe_ID": int(emote_id),
            "TarGet_Uid": (
                int(target_uid) if target_uid is not None else None
            ),
            "boT_Uid": login["uid"],
            "SeNd To": sent_to,
            "message": "Emote sent successfully; TCP closed after 4 seconds"
        }

    finally:
        if bot is not None and bot.online is not None:
            bot.online.close()
            print("[api] Online TCP connection closed")


@app.get("/rishu")
def rishu_endpoint():
    team_code = (request.args.get("Tc") or "").strip()
    emote_value = (request.args.get("Emote_id") or "").strip()
    target_value = (
    request.args.get("Target_Uid")
    or request.args.get("Target_uid")
    or request.args.get("target_uid")
    or ""
).strip()
    if not team_code.isdigit():
        return jsonify(ok=False, error="Tc must be a numeric team code"), 400
    if not emote_value:
        emote_value = str(DEFAULT_EMOTE_ID)
    if not emote_value.isdigit():
        return jsonify(ok=False, error="Emote_id must be a numeric emote ID"), 400
    if target_value and not target_value.isdigit():
        return jsonify(ok=False, error="Target_Uid must be numeric"), 400
    try:
        with _api_lock:
            result = run_api_emote(team_code, int(emote_value), int(target_value) if target_value else None)
        return jsonify(result), 200
    except Exception as exc:
        print("[api] request failed:", exc)
        return jsonify(ok=False, error=str(exc)), 500

# -------------------------------------------------------------------- server ----
if __name__ == "__main__":
    selftest()


    if not BOT_UID or not BOT_PASSWORD:
        raise SystemExit("BOT_UID or BOT_PASSWORD missing")

    print("[RISHU] Flask API starting")
    print("[RISHU] Endpoint: /rishu?Tc=3773&Emote_id=909000001&Target_Uid=123456789")
    print("[RISHU] Empty Emote_id uses default ID:", DEFAULT_EMOTE_ID)
    print("[RISHU] Rishu Emote Bot")

    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        threaded=True
    )
