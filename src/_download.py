"""Small resumable HTTP downloader shared by the get_*.py scripts."""
import hashlib, os, sys, time
from pathlib import Path
import requests

from paths import ROOT, RAW  # noqa: F401


def fetch(url, dest, expected_size=None, chunk=1 << 22):
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and (expected_size is None or dest.stat().st_size == expected_size):
        print(f"[skip] {dest.name} ({dest.stat().st_size/1e6:.1f} MB)")
        return dest
    tmp = dest.with_suffix(dest.suffix + ".part")
    pos = tmp.stat().st_size if tmp.exists() else 0
    headers = {"Range": f"bytes={pos}-"} if pos else {}
    t0 = time.time()
    with requests.get(url, headers=headers, stream=True, timeout=120) as r:
        if r.status_code not in (200, 206):
            raise RuntimeError(f"{url}: HTTP {r.status_code}")
        if r.status_code == 200:
            pos = 0
        with open(tmp, "ab" if pos else "wb") as f:
            for b in r.iter_content(chunk):
                f.write(b)
    tmp.rename(dest)
    size = dest.stat().st_size
    if expected_size is not None and size != expected_size:
        raise RuntimeError(f"{dest.name}: size {size} != expected {expected_size}")
    print(f"[ok] {dest.name} {size/1e6:.1f} MB in {time.time()-t0:.0f}s")
    return dest


def md5(path, chunk=1 << 22):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def fetch_parallel(url, dest, n_conn=8, chunk=8 << 20, retries=20):
    """Multi-connection ranged download with per-chunk resume (sidecar .chunks file).
    Each request re-resolves `url` (fresh signed redirect), so long downloads survive URL expiry."""
    import json, threading
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        print(f"[skip] {dest.name}")
        return dest
    r = requests.get(url, headers={"Range": "bytes=0-0"}, stream=True, timeout=120)
    size = int(r.headers["Content-Range"].split("/")[-1])
    r.close()
    part = dest.with_suffix(dest.suffix + ".ppart")
    side = dest.with_suffix(dest.suffix + ".chunks")
    done = set(json.load(open(side))) if side.exists() else set()
    if not part.exists():
        with open(part, "wb") as f:
            f.truncate(size)
    todo = [i for i in range((size + chunk - 1) // chunk) if i not in done]
    lock = threading.Lock()
    t0 = time.time()

    def worker():
        while True:
            with lock:
                if not todo:
                    return
                i = todo.pop(0)
            a, b = i * chunk, min(size, (i + 1) * chunk) - 1
            for _ in range(retries):
                try:
                    rr = requests.get(url, headers={"Range": f"bytes={a}-{b}"}, timeout=120)
                    if rr.status_code == 206 and len(rr.content) == b - a + 1:
                        with lock:
                            with open(part, "r+b") as f:
                                f.seek(a)
                                f.write(rr.content)
                            done.add(i)
                            json.dump(sorted(done), open(side, "w"))
                        break
                except requests.RequestException:
                    pass
                time.sleep(3)
            else:
                raise RuntimeError(f"chunk {i} failed")

    th = [threading.Thread(target=worker) for _ in range(n_conn)]
    [t.start() for t in th]
    [t.join() for t in th]
    part.rename(dest)
    side.unlink(missing_ok=True)
    print(f"[ok] {dest.name} {size/1e6:.1f} MB in {time.time()-t0:.0f}s ({n_conn} connections)")
    return dest
