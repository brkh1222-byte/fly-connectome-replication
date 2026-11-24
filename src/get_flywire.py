"""T1.1: FlyWire v783 (female brain).

Sources (all CC BY 4.0 unless noted):
  * Zenodo 10.5281/zenodo.10676866 (FlyWire connectivity v783): proofread_connections_783.feather
    and proofread_root_ids_783.npy.
  * Shiu et al. model inputs (github.com/philshiu/Drosophila_brain_model, MIT, commit 91bdd1e):
    Completeness_783.csv, Connectivity_783.parquet (and the v630 equivalents). Cloned into
    data/external/shiu_repo.
  * Cell-type annotations: Schlegel et al. 2024, github.com/flyconnectome/flywire_annotations,
    Supplemental_file1_neuron_annotations.tsv (v783).
Usage: python src/get_flywire.py
"""
import subprocess
from _download import RAW, fetch
from paths import SHIU

ZENODO = "https://zenodo.org/api/records/10676866/files/{}/content"
FILES = {"proofread_connections_783.feather": 852_000_000, "proofread_root_ids_783.npy": None}
ANNOT = ("https://raw.githubusercontent.com/flyconnectome/flywire_annotations/main/"
         "supplemental_files/Supplemental_file1_neuron_annotations.tsv")
SHIU_URL = "https://github.com/philshiu/Drosophila_brain_model.git"
SHIU_COMMIT = "91bdd1e7dcf193f3e7ca5a8933497fcef63b7960"

if __name__ == "__main__":
    import sys
    out = RAW / "flywire_783"
    if "--zenodo" in sys.argv:  # optional: the model itself uses Shiu's derived v783 table
        for f in FILES:
            fetch(ZENODO.format(f), out / f)
    fetch(ANNOT, out / "Supplemental_file1_neuron_annotations.tsv")
    repo = SHIU
    repo.parent.mkdir(parents=True, exist_ok=True)
    if not repo.exists():
        subprocess.run(["git", "clone", SHIU_URL, str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "checkout", "-q", SHIU_COMMIT], check=True)
    print("done")
