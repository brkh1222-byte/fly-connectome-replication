# Licence decision (T0.2)

**Decision (2026-11-24): this repository is MIT-licensed.**

- Shiu et al.'s model code (github.com/philshiu/Drosophila_brain_model) is MIT. We may reuse
  and adapt it with attribution. The reproduction script `src/shiu_brian2.py` follows the
  structure and parameters of their `model.py`; the MIT notice for that work is kept in
  `THIRD_PARTY_NOTICES.md`.
- The PyTorch simulator `src/lif_torch.py` is our own reimplementation, written from the
  equations in Shiu et al. (2024, Methods) and their MIT Brian2 code.
- We did **not** open or copy any code from eonsystemspbc/fly-brain (GPL-2.0-or-later), and we
  must not do so in future. Doing so would force the repository to become GPL.
- Data are not code. FlyWire, BANC and male CNS releases are CC BY 4.0 and must be cited.
  They are git-ignored and never committed. Check each annotation file's licence before use;
  some FlyWire-derived files are reported to be CC BY-NC.
