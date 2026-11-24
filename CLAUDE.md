# CLAUDE.md

This is a research project by an independent researcher. It tests whether the Shiu et al. 2024 whole-brain Drosophila LIF model's predictions replicate on other individuals' connectomes (FlyWire v783 vs BANC vs the male CNS). Read PROPOSAL.md first.

- **Data access:** prefer the versioned public releases (Zenodo, the Janelia GCS bucket, Harvard Dataverse) so results are reproducible. flywire.ai, Codex and CAVE may be used if a file is only available there.
- **Compute:** big sweeps run on a remote H100. Keep everything runnable on CPU with small settings for testing. Connectome files under `data/` are git-ignored.
- **Licences:** Shiu's code is MIT. eonsystemspbc/fly-brain is GPL-2.0+; don't copy from it unless the repo licence is GPL (see `notes/licence.md`). Cite all datasets (CC BY 4.0).
- **Validation first:** never run cross-connectome experiments until the PyTorch LIF matches Brian2 on FlyWire.
- **Integrity / authorship:** Claude drafts the paper; the researcher reviews and edits it; the paper carries an AI-use disclosure. Authorship is undecided: use the placeholders `[AUTHORS — TBD]` and `[AI-USE STATEMENT — TBD]`. Explain methods when implementing them. Verify every citation. Report failures faithfully.
