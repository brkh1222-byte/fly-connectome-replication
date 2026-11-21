# CLAUDE.md

This is a research project by a 17-year-old student. It tests whether the Shiu et al. 2024 whole-brain Drosophila LIF model's predictions replicate on other individuals' connectomes (FlyWire v783 vs BANC vs the male CNS). Read PROPOSAL.md first.

- **Data access:** use Zenodo, the Janelia GCS bucket and Harvard Dataverse. **Do not use flywire.ai, Codex or CAVE**: their terms need parent or guardian consent for users under 18.
- **Compute:** big sweeps run on a remote H100. Keep everything runnable on CPU with small settings for testing. Connectome files under `data/` are git-ignored.
- **Licences:** Shiu's code is MIT. eonsystemspbc/fly-brain is GPL-2.0+; don't copy from it unless the repo licence is GPL (see `notes/licence.md`). Cite all datasets (CC BY 4.0).
- **Validation first:** never run cross-connectome experiments until the PyTorch LIF matches Brian2 on FlyWire.
- **Integrity:** the student must understand and write the paper themselves. Explain methods when implementing them. Verify every citation.
