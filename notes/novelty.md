# Novelty check (2026-11-24)

The search was run by a helper agent and re-checked by the pilot. Sources marked "opened"
were read directly; the rest were seen only in search snippets.

## Verdict: PARTIALLY OVERLAPPED (heavily), not scooped

No paper, preprint or repository runs Shiu et al.'s validated predictions on **all three**
connectomes (FlyWire v783, BANC v888, male CNS v1.0) with null models, a completeness
control and formal statistics. However, the FlyWire-vs-BANC half of the study, including a
hemisphere "ladder", has already been posted.

| Item | Date | What it did | Overlap | Checked |
|---|---|---|---|---|
| **amthedev/cerebro-mosca** (A. M. S. Santos), Zenodo 10.5281/zenodo.23005090, MIT; draft preprint in Portuguese | 28 Sep 2026 | Exact numba re-implementation of the Shiu LIF (r = 0.999 vs Brian2), run on FlyWire v783 and BANC v888 (7 synapse-table versions). Per-type Spearman ladder: repeat-seed 0.98, left-right hemisphere 0.54, FlyWire-BANC ≤ 0.32. BANC as-is loses sugar→MN9 and JO→aBN1 but keeps looming→giant fiber. Per-type calibration restores sugar but not JO→aBN1. Reports Brian2 discarding input during refractoriness, a sign error on il3LN6 in the v630 model file, and BANC NT-consensus errors. | **High** for FlyWire-BANC | Opened (GitHub README, repo metadata); Zenodo record seen via the helper agent |
| Pronexsteam/brainlab; htem/BANC-project issue #1 | Sep 2026 | Unchanged Shiu model on FlyWire v783 / male CNS **v0.9** / BANC v888: sugar→MN9 76.7 / 68.9 / 17.8 Hz; BANC path cells get about 0.35-0.39x the input synapses. No statistics, nulls or hemisphere baseline. | High (sugar only) | Opened (helper) |
| vichienFF/flybrain-connectome-benchmark; Zenodo 10.5281/zenodo.23025559 | Sep-Oct 2026 | FlyWire benchmark against 16 findings. Pre-registered male CNS v1.0 replication: sugar→MN9 34 Hz after recalibration; water→MN9 not evaluable in the male CNS. | Medium | Opened (helper) |
| Yad & Nabila, arXiv:2610.29205 | Oct 2026 | Compass circuit only; reconstruction differences rival individual differences | Low-medium | Abstract opened (helper) |
| Minnick et al., arXiv:2610.33881 | Oct-Nov 2026 | Shiu-style model on BANC in a virtual body; weak sugar→MN9 | Low | Abstract opened (helper) |
| An, bioRxiv 10.64898/2026.09.19.752860 (FlyLite) | Sep 2026 | Edge pruning and shuffles on FlyWire v630 only | Low (relevant to the degradation control) | Snippet only |
| Liu, arXiv:2611.14508; Guan et al., arXiv:2609.38665; Asis, arXiv:2611.09930 | 2026 | Real vs shuffled wiring; leg circuits; odour learning | Low | Abstracts (helper) |
| annel0/flybrain, igdigitallab/bioreservoir, alextitonis/fly.ai, flymsg, drosophila-brain-mlx, opifor/femaleflybrain, indian-aman/drosophila-whole-cns-specificity | 2026 | Ports, tooling, within-connectome work | Low | Mixed |

## What remains novel (and becomes our framing; see decisions.md D1)

1. The **male CNS v1.0** rung, run with the same pipeline and the same statistics as the
   female-female comparison.
2. **Water → MN9** and **bitter suppression** tested on all three connectomes.
3. **Degree-preserving shuffle nulls** run on every connectome, which gives a floor for the
   cross-connectome agreement.
4. A **degraded-FlyWire completeness control**: does thinning FlyWire to BANC-like per-type
   input counts reproduce BANC's failures? Nobody has done this for a whole-brain model.
5. A **pre-specified robustness sweep**: normalisations × thresholds × seeds, with verdicts
   rather than single numbers.
