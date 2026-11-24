# Novelty check and precise comparison with prior work (updated 2026-11-24)

The search was run by a helper agent. The pilot then re-checked the key items: it read the
cerebro-mosca README, its draft preprint (`artigo/preprint.md`) and its bioRxiv submission
form, all on GitHub. Items marked "snippet" were not opened.

## 1. cerebro-mosca (the closest prior work)

**Citation:** Santos, A. M. S. (2026). *Auditing a whole-brain Drosophila model across
hemispheres and individuals: a single mis-signed neuron, a non-sparse olfactory regime, and
limited cross-connectome reproducibility.* Preprint draft, Sep 2026, **not peer reviewed**.
Code and data: github.com/amthedev/cerebro-mosca (MIT), archived at Zenodo
doi:10.5281/zenodo.23005090 (v1.0.0, 28 Sep 2026). The repo has a bioRxiv submission form. No
bioRxiv or journal record was found by search on 24 Nov 2026. The draft discloses AI
assistance (Claude).

**Model:** an exact event-driven reimplementation of Shiu's LIF (numba). It reproduces Brian2's
"unless refractory" input discarding; r = 0.999 vs Brian2; MN9 77.7 vs 78.8 Hz at 150 Hz sugar.

**Connectomes:** FlyWire v783 (Shiu's model file) and the brain portion of **BANC v888**
(151,000 neurons). They tried seven BANC variants: the v2 and v3 edge lists, × global rescale /
per-type calibration / type-level signs. **No male CNS.**

**Experiments:**
- **Audit of FlyWire:** sugar → MN9 and four named interneurons; bitter veto; Ir94e partial
  veto; JO-CE → aBN1 (70 Hz) vs JO-F (0 Hz); LPLC2 → giant fiber. All hold under four
  "biological corrections" to signs and modulators.
- **New FlyWire problems:** odour drives 66% of Kenyon cells. Stimulating right-side sugar
  GRNs recruits 8,323 neurons (vs 446 on the left), caused by one mis-signed il3LN6 neuron.
  2,607 neurons in Shiu's file have signs that contradict literature transmitters.
- **Weight sweep:** 0.7–1.5× W_syn. FlyWire is stable; BANC runs away at about 1.4–1.8×.
- **FlyWire vs BANC:** six protocols (sugar LB3, bitter LB1a–d, food odour, CO2, LPLC2,
  JO-C/E), each on both sides.

**Metrics:** per-(type, side) mean rate, with stimulated types excluded. They report the
Spearman ρ over types active (> 2 Hz) in either condition, and the Jaccard index of the active
sets. Rungs: repeat seed ρ = 0.98; hemispheres ρ = 0.54 (FlyWire) / 0.47 (BANC); FlyWire vs
BANC ρ ≤ 0.32 (Jaccard 0.28) in every variant. No confidence intervals, no significance
tests, and **no null model**: it is not shown whether 0.32 exceeds chance.

**Findings on BANC:**
- BANC as-is fails sugar → MN9 and JO → aBN1 and keeps looming → giant fiber.
- Synapses per neuron are 2.1× lower (v2) and 1.7× lower (v3). The deficit is regional:
  2.5× on MN9 inputs.
- 7% of matched types disagree in transmitter sign.
- Per-type calibration with type-level signs restores sugar → MN9 (21.5–46 Hz) but not
  JO → aBN1.
- The BANC NT-consensus column contradicts neuron-level predictions for 68 types.
- Their interpretation: "this difference reflects synapse detection and size thresholds, not
  necessarily biology." They assert this but **do not test it causally**.

## 2. Other prior work

| Item | What it did | Overlap |
|---|---|---|
| Pronexsteam/brainlab (GitHub, Sep 2026; htem/BANC-project issue #1) | Unchanged Shiu model; sugar→MN9 76.7 / 68.9 / 17.8 Hz on FlyWire / male CNS **v0.9** / BANC. No statistics, no hemispheres, no nulls. | Sugar only |
| vichienFF/flybrain-connectome-benchmark (Zenodo 10.5281/zenodo.23025559, Oct 2026) | FlyWire benchmark (11/16 findings pass). Pre-registered male CNS **v1.0** replication: sugar→MN9 34 Hz after recalibration; water→MN9 "not evaluable". | Male CNS sugar; no cross-connectome agreement or ladder |
| Yad & Nabila, arXiv:2610.29205 | Compass circuit; reconstruction differences rival individual differences; trained models do not transfer | Same question, one small circuit, not Shiu's model |
| Minnick et al., arXiv:2610.33881 | Shiu-style BANC model in a body; weak sugar→MN9 | Low |
| An (FlyLite), bioRxiv 10.64898/2026.09.19.752860 | Edge pruning and shuffles on FlyWire v630 only (snippet) | Methodological precedent for degradation and shuffles |
| Others (Liu arXiv:2611.14508; Guan arXiv:2609.38665; Asis arXiv:2611.09930; flymsg; drosophila-brain-mlx; opifor; indian-aman; annel0; bioreservoir; fly.ai) | Tooling, within-connectome work, real-vs-shuffled theory | Low |

## 3. What remains new for us (honest assessment)

| Element | Status in prior work | New here? |
|---|---|---|
| Shiu predictions on FlyWire vs BANC | cerebro-mosca (thorough), brainlab | **No.** It becomes an independent replication of their result |
| Seed / hemisphere / between-fly ladder | cerebro-mosca (FlyWire-BANC only, no CIs) | **Partly.** New: a third connectome, bootstrap CIs, nulls |
| Male CNS v1.0 in the same pipeline and ladder | brainlab (v0.9, sugar only); vichienFF (sugar, own calibration, no agreement metrics) | **Yes** for the ladder and multi-prediction test, but not for sugar→MN9 alone |
| **Three-way "triangle":** FlyWire-BANC vs FlyWire-maleCNS vs BANC-maleCNS | None | **Yes.** It separates the two-female pair from the different-lab and different-sex pairs |
| **Degraded-FlyWire completeness control** (thin FlyWire to BANC's per-type synapse deficit, then ask whether it reproduces BANC's failures and its ρ) | Asserted by cerebro-mosca, not tested; FlyLite pruned FlyWire for other reasons | **Yes.** This is the clearest distinct contribution |
| **Degree-preserving shuffle nulls** per connectome (is ρ = 0.32 above chance?) | None | **Yes** |
| Water → MN9 on all three | vichienFF: not evaluable in the male CNS | **Yes** (small) |
| Threshold × normalisation × seed robustness with verdicts | cerebro-mosca swept W_syn only | **Yes** (incremental) |
| Stimulation screen over all matched sensory types × 3 connectomes | None (cerebro-mosca used 6 protocols) | **Yes**, with moderate interest |
| NT-sign audit, il3LN6 bug | cerebro-mosca | **No.** We cite it and check whether il3LN6 affects our protocols |

**Verdict:** the remaining novelty is **real but moderate, not thin**. The descriptive
headline "FlyWire and BANC disagree; hemispheres agree better" is taken. What is not taken
is the explanation and calibration of that disagreement:
(i) is it above a shuffled-network floor;
(ii) can reconstruction incompleteness alone (degraded FlyWire) reproduce it;
(iii) does a third, independently reconstructed and highly complete connectome (male CNS)
agree with FlyWire better or worse than BANC does, despite being male?

## 4. Proposed framing (decision D1-revised, notes/decisions.md)

**Working title:** *Reconstruction, not individuality? Completeness-matched controls explain
cross-connectome disagreement in a whole-brain Drosophila model.* (The title will be adjusted
to the actual result; if degradation does not explain the gap, the title flips.)

- **Introduction:** present cerebro-mosca and brainlab up front as having shown that the
  Shiu model's predictions transfer poorly from FlyWire to BANC. State the open question they
  leave: is that disagreement biological or technical?
- **Results 1:** port validation (float32 vs Brian2), and reproduction of Shiu on FlyWire.
- **Results 2:** an independent replication of the FlyWire-BANC gap. We present this as
  confirming cerebro-mosca, with our numbers next to theirs.
- **Results 3:** the new male CNS rung and the three-way triangle.
- **Results 4:** shuffle floor and bootstrap CIs.
- **Results 5:** degraded-FlyWire control (headline).
- **Results 6:** robustness sweep; stimulation screen.

**Ranked framing options for the researcher:**
1. **(Recommended) "Explaining the gap"**, as above: the degraded-FlyWire control and the
   three-connectome triangle are the headline. Most distinct from prior work, and it gives an
   interpretable answer whatever the outcome.
2. **"Robustness atlas"**: the stimulation screen across three connectomes, with nulls, as
   the headline (which predictions transfer). It is useful to experimentalists, but less
   conceptually sharp and closer to cerebro-mosca's "robust predictions replicate" message.
3. **"Independent replication + male CNS extension"**: a short replication report (RSOS
   replication track, or ReScience C-style). It is the safest and fastest, but the least
   novel.
