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
