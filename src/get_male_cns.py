"""T1.2: male CNS v1.0 (Berg et al. 2026, Cell), anonymous HTTPS from the public Janelia
bucket gs://flyem-male-cns/v1.0/connectome-data/flat-connectome/ (CC BY 4.0)."""
from _download import RAW, fetch

BASE = "https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/"
# Small files first. We use the "traced-only" weights: edges between bodies with Traced status,
# the analogue of FlyWire's proofread-only connectivity (and half the size of the full table).
FILES = {
    "body-annotations-male-cns-v1.0-minconf-0.5.feather": None,
    "body-neurotransmitters-male-cns-v1.0.feather": None,
    "connectome-weights-male-cns-v1.0-minconf-0.5-traced-only.feather": None,
}
if __name__ == "__main__":
    for f in FILES:
        fetch(BASE + f, RAW / "male_cns_v1.0" / f)
    print("done")
