"""Central paths. Override with env vars on the cloud box:
FLY_DATA (default <repo>/data) and FLY_RESULTS (default <repo>/results)."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get("FLY_DATA", ROOT / "data"))
RESULTS = Path(os.environ.get("FLY_RESULTS", ROOT / "results"))
RAW = DATA / "raw"
STD = DATA / "std"
SHIU = DATA / "external" / "shiu_repo"
