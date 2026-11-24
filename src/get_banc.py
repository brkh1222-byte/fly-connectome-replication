"""T1.3: BANC v888 (Bates et al. 2026, Nature), Harvard Dataverse doi:10.7910/DVN/7WTH1N
(dataset version 3.0, CC BY 4.0). No login is needed for these files; only the raw
chunk_*.parquet files are restricted and they are not used."""
from _download import RAW, fetch

API = "https://dataverse.harvard.edu/api/access/datafile/{}"
# Dataverse file id -> filename (listed 2026-11-24 from the dataset API)
FILES = {  # small files first
    13994485: "banc_fafb_reviewed_matches.csv.gz",
    13994488: "banc_malecns_reviewed_matches.csv.gz",
    13916450: "banc_888_neurotransmitter_prediction_v2.csv",
    14033740: "banc_888_meta.feather",
    13992792: "banc_888_edgelist_simple_v2.feather",
}
OPTIONAL = {13918810: "banc_888_edgelist_simple_v3.feather"}  # synapse-table v3 (robustness)
if __name__ == "__main__":
    import sys
    todo = dict(FILES, **(OPTIONAL if "--v3" in sys.argv else {}))
    for fid, name in todo.items():
        # ?format=original avoids Dataverse's tabular re-ingest for csv files
        fetch(API.format(fid) + "?format=original", RAW / "banc_888" / name)
    print("done")
