#!/usr/bin/env python3
"""
Lock / unlock the SOC instructor edition behind a passphrase.

  Lock:    python3 lock-instructor-edition.py lock   plain.html locked.html "Passphrase"
  Unlock:  python3 lock-instructor-edition.py unlock locked.html plain.html "Passphrase"

Crypto: PBKDF2-HMAC-SHA256 (310,000 iterations) -> AES-256-GCM, matching the
WebCrypto code embedded in the unlock shell. Re-run "lock" any time you edit
the plain file or want to change the passphrase.
"""
import sys, os, json, base64, re
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ITERATIONS = 310_000

def derive(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt,
                     iterations=ITERATIONS)
    return kdf.derive(passphrase.encode("utf-8"))

def lock(src, dst, passphrase):
    with open(src, "r", encoding="utf-8") as f:
        plaintext = f.read().encode("utf-8")
    salt = os.urandom(16)
    iv = os.urandom(12)
    key = derive(passphrase, salt)
    ct = AESGCM(key).encrypt(iv, plaintext, None)
    payload = {
        "v": 1,
        "kdf": "PBKDF2-SHA256",
        "iter": ITERATIONS,
        "salt": base64.b64encode(salt).decode(),
        "iv": base64.b64encode(iv).decode(),
        "ct": base64.b64encode(ct).decode(),
    }
    shell = SHELL_TEMPLATE.replace("__PAYLOAD_JSON__", json.dumps(payload))
    with open(dst, "w", encoding="utf-8") as f:
        f.write(shell)
    print(f"Locked {src} -> {dst} ({len(ct)//1024} KB ciphertext)")

def unlock(src, dst, passphrase):
    with open(src, "r", encoding="utf-8") as f:
        shell = f.read()
    m = re.search(r'<script type="application/json" id="vault">(.*?)</script>',
                  shell, re.S)
    if not m:
        sys.exit("No vault payload found in input file.")
    p = json.loads(m.group(1))
    key = derive(passphrase, base64.b64decode(p["salt"]))
    pt = AESGCM(key).decrypt(base64.b64decode(p["iv"]),
                             base64.b64decode(p["ct"]), None)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(pt.decode("utf-8"))
    print(f"Unlocked {src} -> {dst}")

SHELL_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Instructor edition - passphrase required.">
<meta name="robots" content="noindex">
<title>SOC Training Exercises - Instructor Edition (Locked)</title>
<style>
:root{
  --bg-1:#1a1a2e; --bg-2:#16213e; --surface:rgba(255,255,255,.05);
  --border:rgba(255,255,255,.12); --accent:#a855f7; --accent-2:#7c3aed;
  --cyan:#00d4ff; --text:#e0e0e0; --muted:#9aa6b2; --err:#ff6b6b; --ok:#2ed573;
}
*{margin:0;padding:0;box-sizing:border-box}
body{
  font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;
  background:linear-gradient(135deg,var(--bg-1) 0%,var(--bg-2) 100%);
  min-height:100vh;color:var(--text);
  display:flex;align-items:center;justify-content:center;padding:24px;
}
.card{
  width:100%;max-width:460px;background:var(--surface);
  border:1px solid var(--border);border-radius:14px;padding:36px 32px;
  box-shadow:0 18px 50px rgba(0,0,0,.45);
}
.lock-badge{
  width:64px;height:64px;border-radius:50%;margin:0 auto 18px;
  display:flex;align-items:center;justify-content:center;
  background:rgba(168,85,247,.12);border:1px solid rgba(168,85,247,.4);
  font-size:28px;
}
h1{font-size:1.25rem;text-align:center;margin-bottom:6px;color:#fff}
.sub{color:var(--muted);font-size:.9rem;text-align:center;margin-bottom:26px;line-height:1.5}
label{display:block;font-size:.8rem;letter-spacing:.5px;text-transform:uppercase;
  color:var(--muted);margin-bottom:8px}
input[type="password"]{
  width:100%;min-height:48px;padding:12px 14px;border-radius:8px;
  border:1px solid var(--border);background:rgba(0,0,0,.3);color:var(--text);
  font-size:1rem;
}
input[type="password"]:focus{outline:2px solid var(--accent);outline-offset:2px;border-color:var(--accent)}
button{
  width:100%;min-height:48px;margin-top:16px;border:none;border-radius:8px;
  background:linear-gradient(135deg,var(--accent) 0%,var(--accent-2) 100%);
  color:#fff;font-size:1rem;font-weight:600;cursor:pointer;font-family:inherit;
}
button:focus-visible{outline:2px solid var(--cyan);outline-offset:3px}
button:hover{filter:brightness(1.1)}
button[disabled]{opacity:.6;cursor:wait}
.msg{min-height:22px;margin-top:14px;font-size:.88rem;text-align:center}
.msg.err{color:var(--err)}
.msg.ok{color:var(--ok)}
.hint{margin-top:22px;padding-top:16px;border-top:1px solid var(--border);
  color:var(--muted);font-size:.78rem;text-align:center;line-height:1.5}
@media (prefers-reduced-motion: no-preference){
  .card{animation:rise .35s ease}
  @keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
}
</style>
</head>
<body>
<main class="card" aria-labelledby="lockTitle">
  <div class="lock-badge" aria-hidden="true">&#128274;</div>
  <h1 id="lockTitle">Instructor Edition</h1>
  <p class="sub">This document is encrypted. Enter the instructor passphrase to unlock the exercises, answer keys, rubrics, and teaching notes.</p>
  <form id="unlockForm">
    <label for="pw">Instructor passphrase</label>
    <input type="password" id="pw" autocomplete="current-password" autofocus>
    <button type="submit" id="unlockBtn">Unlock</button>
  </form>
  <p class="msg" id="msg" role="status" aria-live="polite"></p>
  <p class="hint">Students: please use the Student Edition from the SOC hub.<br>
  Access issues? Contact your instructor or program coordinator.</p>
</main>

<script type="application/json" id="vault">__PAYLOAD_JSON__</script>
<script>
(function(){
  var form = document.getElementById('unlockForm');
  var pwEl = document.getElementById('pw');
  var btn  = document.getElementById('unlockBtn');
  var msg  = document.getElementById('msg');
  var vault = JSON.parse(document.getElementById('vault').textContent);

  function setMsg(text, cls){ msg.textContent = text; msg.className = 'msg' + (cls ? ' ' + cls : ''); }
  function b64ToBuf(b64){
    var bin = atob(b64), buf = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
    return buf;
  }

  if (!(window.crypto && crypto.subtle)) {
    setMsg('This page requires a secure context (open the file directly, or serve over HTTPS/localhost).', 'err');
    btn.disabled = true;
    return;
  }

  async function tryUnlock(passphrase, silent){
    btn.disabled = true;
    if (!silent) setMsg('Decrypting\u2026');
    try {
      var enc = new TextEncoder();
      var baseKey = await crypto.subtle.importKey('raw', enc.encode(passphrase),
        'PBKDF2', false, ['deriveKey']);
      var key = await crypto.subtle.deriveKey(
        { name:'PBKDF2', salt:b64ToBuf(vault.salt), iterations:vault.iter, hash:'SHA-256' },
        baseKey, { name:'AES-GCM', length:256 }, false, ['decrypt']);
      var plain = await crypto.subtle.decrypt(
        { name:'AES-GCM', iv:b64ToBuf(vault.iv) }, key, b64ToBuf(vault.ct));
      try { sessionStorage.setItem('soc-instructor-pass', passphrase); } catch(e){}
      var html = new TextDecoder().decode(plain);
      document.open();
      document.write(html);
      document.close();
    } catch (e) {
      btn.disabled = false;
      if (!silent) {
        setMsg('Incorrect passphrase. Please try again.', 'err');
        pwEl.select();
      } else {
        setMsg('');
      }
    }
  }

  form.addEventListener('submit', function(ev){
    ev.preventDefault();
    var pw = pwEl.value;
    if (!pw) { setMsg('Enter the passphrase to continue.', 'err'); return; }
    tryUnlock(pw, false);
  });

  // Re-unlock automatically within the same browser session.
  try {
    var cached = sessionStorage.getItem('soc-instructor-pass');
    if (cached) tryUnlock(cached, true);
  } catch(e){}
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    if len(sys.argv) != 5 or sys.argv[1] not in ("lock", "unlock"):
        sys.exit(__doc__)
    mode, src, dst, pw = sys.argv[1:5]
    (lock if mode == "lock" else unlock)(src, dst, pw)
