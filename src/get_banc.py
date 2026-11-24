"""T1.3: BANC v888 (Bates et al. 2026, Nature), Harvard Dataverse doi:10.7910/DVN/7WTH1N
(dataset version 3.0, CC BY 4.0). No login is needed for these files; only the raw
chunk_*.parquet files are restricted and they are not used."""
from _download import RAW, fetch, fetch_parallel, md5

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
# The edge list is also on the BANC team's public GCS bucket (referenced from
# github.com/sjcabs/fly_connectome_data_tutorial), which is much faster than Dataverse's S3.
# Its MD5 equals the Dataverse file's (checked 2026-11-24), so we fetch it from GCS and verify.
# The meta / NT files on GCS are newer live versions and are NOT used.
GCS = "https://storage.googleapis.com/lee-lab_brain-and-nerve-cord-fly-connectome/compiled_data/banc_888/"
DV_MD5 = {"banc_888_edgelist_simple_v2.feather": "394406f8a9bdf093c895f95aff4f6c49",
          "banc_888_edgelist_simple_v3.feather": None}

if __name__ == "__main__":
    import sys
    todo = dict(FILES, **(OPTIONAL if "--v3" in sys.argv else {}))
    for fid, name in todo.items():
        # ?format=original avoids Dataverse's tabular re-ingest for csv files.
        # Large files use parallel ranged requests (S3 throughput per connection is low).
        url = API.format(fid) + "?format=original"
        dest = RAW / "banc_888" / name
        if name in DV_MD5:
            fetch(GCS + name, dest)
            if DV_MD5[name] and md5(dest) != DV_MD5[name]:
                raise RuntimeError(f"{name}: MD5 mismatch with the Dataverse release")
        elif name.endswith(".feather"):
            fetch_parallel(url, dest)
        else:
            fetch(url, dest)
    print("done")
