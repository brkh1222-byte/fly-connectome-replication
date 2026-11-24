# Decisions log

Choices that belong to the researcher but were made by Claude so that work would not block.
Each entry gives the choice, the alternatives, and the reason. Any of them can be overridden.

## D1. Not a pivot; reframe around what is still novel (2026-11-24)
**Context:** the novelty check (notes/novelty.md) found cerebro-mosca (Zenodo
10.5281/zenodo.23005090, Sep 2026). It already ran the Shiu model on FlyWire vs BANC with a
seed/hemisphere/cross-fly agreement ladder (ρ = 0.98 / 0.54 / ≤ 0.32), and brainlab ran
sugar→MN9 on all three connectomes (male CNS v0.9).
**Decision:** continue rather than stop. Make the paper's contribution the parts nobody has
done: (i) the male CNS v1.0 rung; (ii) water and bitter predictions on all three
connectomes; (iii) degree-preserving shuffle nulls run on each connectome; (iv) the
degraded-FlyWire completeness control as the headline test of "reconstruction vs
individuality"; (v) a pre-specified robustness sweep. cerebro-mosca and brainlab are cited
prominently as prior, independent replications of the FlyWire-BANC result, and their numbers
are compared with ours.
**Alternatives:** (a) a stimulation-screen "robustness atlas" as the headline; (b) a
transferable calibration method. Both stay available as follow-ups. (a) is partly included
as T4.3.

## D1-revised. Framing: "explaining the cross-connectome gap" (2026-11-24, after reading cerebro-mosca in full)
cerebro-mosca's draft covers FlyWire-vs-BANC very thoroughly: six protocols, a hemisphere
ladder, calibrations, and an NT audit. Our primary contribution is therefore (a) the
degraded-FlyWire completeness control, (b) the three-connectome triangle that adds the male
CNS v1.0, and (c) shuffle floors and CIs. The FlyWire-BANC battery is presented as an
independent replication of cerebro-mosca. Full comparison and ranked options: notes/novelty.md §3–4.

## D2. Simulator semantics follow Brian2 as measured, including its quirks
Brian2 discards synaptic input that arrives during a neuron's refractory period
(notes/brian2_semantics.md). This is arguably a quirk of how `(unless refractory)` interacts
with `on_pre`, not a biological choice. We keep it, because the goal is to replicate Shiu's
model exactly. The PyTorch port reproduces it.

## D3. Validation criteria (fixed before running the comparison)
Three experiments on FlyWire v783 (sugar 100 Hz → MN9; sugar 100 + bitter 100 Hz → MN9;
JO-CE 100 Hz → aBN1), each run with 30 trials × 1 s. Pass if Torch-vs-Brian2 per-neuron rate
correlation ≥ (Brian2-vs-Brian2 seed ceiling − 0.01), the readout 95% CIs overlap, and total
spike counts do not differ (Mann-Whitney p > 0.01). The proposal's original r > 0.99 is
reported too, but the binding criterion is relative to the seed ceiling. With 30 trials,
sampling noise alone can push r below 0.99.

## D4. Male CNS edge table: "traced-only"
Use `connectome-weights-male-cns-v1.0-minconf-0.5-traced-only.feather`: edges between Traced
bodies, synapse confidence ≥ 0.5. This is the closest analogue of FlyWire's proofread-only
graph, and it is half the size of the full table (network bandwidth was about 140 KB/s).

## D5. The FlyWire model graph is Shiu's own v783 table
The FlyWire network is Shiu's `Connectivity_783.parquet` (derived from the Zenodo v783
release), so that our FlyWire baseline is exactly the published model. The Zenodo file
`proofread_connections_783.feather` is optional (`get_flywire.py --zenodo`); it is used only
for a derivation check if it can be downloaded.

## D6. Compute plan (revised 2026-11-24): Mac for main analyses, one rented RTX 4090 for sweeps
The researcher will rent one RTX 4090 (24 GB). The Mac (Apple M4, 16 GB shared with three
other agents) runs: data, Brian2 reproduction, validation, matching, the main
cross-connectome experiments (3 datasets × N0/N1/N2, core battery + replicate seed), and the
degraded-FlyWire control if time allows. The 4090 runs the full grid in `src/sweep.py`:
- **P1 (T4.2):** 50 degraded copies per reference × {N0, N1}; 50 shuffles per dataset × {N0, N1}.
  Fifty copies give a stable 95% range (2.5th-97.5th percentile) for a null distribution;
  20 would leave the tails resting on one or two values.
- **P2 (T4.1):** thresholds {1, 3, 5, 10} cover "all synapses" (Shiu) through the common
  "≥ 5" convention to a strict 10. All three normalisations; three sign schemes; brain plus
  whole CNS. Each base setting gets a replicate seed (the seed rung). The 10 edge-noise
  bootstraps per own-sign setting estimate the uncertainty that comes from the connectome
  itself. Ten replicates are enough to estimate a spread at the scale of agreement
  differences (about 0.05 in ρ).
- **P3 (T4.3):** every sensory type shared by the three datasets and present on both sides,
  stimulated alone at 150 Hz, with 5 shuffle controls per dataset.
Seeds: within each item, trials are independent seeds (30, as in Shiu). Replicate seeds are
separate items.

## D7. Pre-specified analysis (fixed before any cross-connectome simulation)
- Protocol rate is 150 Hz (Shiu's default `r_poi`) for every stimulus. Rate curves are
  supplementary.
- Replication criteria: see src/analysis.py docstring (≥ 5 Hz and ≥ 20% of FlyWire, Wilcoxon
  vs 0; suppression ≥ 50% with Mann-Whitney; JO-CE > JO-F with Mann-Whitney; Holm across
  non-FlyWire tests).
- Agreement: per (type, side relative to stimulus) mean rate; Spearman on log1p over groups
  active ≥ 2 Hz in either profile; Jaccard; top-20/50 overlap. The 2 Hz threshold and the
  group definition follow cerebro-mosca, so numbers are comparable.
- Primary setting: brain subgraph, all synapses (threshold 1), N1, own signs.
- **H3 completeness test:** the FlyWire-BANC ρ is "explained by completeness" if it falls
  inside the 2.5-97.5% range of the FlyWire-vs-degraded-FlyWire(→BANC) distribution. The
  test is run under N0 (as-is) and N1.

## D8. Stimulus sets are defined by cell type, identically in every dataset
Shiu's hand-picked v630 neuron lists do not exist in BANC or the male CNS, and in v783 their
"sugar" list mixes LB3b/c/d and LB4b. Cross-connectome stimuli therefore use type definitions
(sugar = LB3b + LB3c, bitter = LB1a-d, water = LB3a, JO-CE = JO-C*/JO-E*, JO-F = JO-F*) on each
side. The FlyWire reproduction uses Shiu's exact lists.

## D9. Signs: Shiu's file for FlyWire; each dataset's own predictions otherwise
Shiu's v783 signs disagree with Schlegel's top_nt for about 6,000 neurons. Among them is
il3LN6, which cerebro-mosca showed causes a right-side sugar runaway; our 100 ms smoke test
reproduced it. The primary analysis keeps Shiu's signs, since the aim is to replicate the
published model. The "nt" and "type" sign schemes are run in the sweep, and the hemisphere
rung is reported under both "own" and "nt" signs.

## Researcher's choices (2026-11-25, relayed by the coordinator)
- Framing (a): "explaining the FlyWire-BANC gap"; the degraded-FlyWire test and three
  connectomes are the headline; cerebro-mosca is cited prominently.
- Cloud: rent one RTX 4090 and run the full grid (the researcher rents; Claude drives over SSH).
- Signs: Shiu's own signs are the main result; the transmitter-rule variant is reported alongside.

## D10. Lopsided BANC sensory typing in hemisphere analyses
BANC's typed sensory neurons are unbalanced by side (water 3 L vs 15 R; JO-F 37 vs 108; sugar
32 vs 45). The BANC hemisphere rung is reported per protocol with water and JO-F flagged, and
repeated with the larger side randomly subsampled to the smaller side's count. Between-fly
comparisons use the same side in both connectomes, so they are also affected for water-L;
this is listed as a limitation.

## D11. "Runaway" label and what the first N1 results showed (2026-11-25, preliminary)
In the first N1 runs, some protocols put a network into a brain-wide active state (8,000 to
13,000 active neurons, versus under about 1,300 otherwise): FlyWire right sugar (the known
il3LN6 sign error), BANC left JO-CE / right sugar / right water, and male CNS bitter (both
sides) / left JO-CE. Agreement metrics are dominated by whether both networks are in the same
regime. We therefore (i) report a descriptive `runaway` flag per experiment (more than 2% of
brain neurons active; results/activity_table.csv), chosen after seeing the data and labelled
as such; (ii) keep the pre-specified metrics unchanged; and (iii) additionally report ladder
medians restricted to pairs where neither network is in runaway, marked exploratory.
Male CNS neurons with transmitter "unclear" (14,365) are excitatory under Shiu's rule ("all
others excitatory"); this is kept and listed as a limitation.

## D12. A second, CPU worker for preliminary nulls
Once the Brian2 reproduction finishes, a CPU job runs degrade/shuffle seeds 2 and 1 while the
MPS queue runs seeds 0 upward (two heavy processes in total). Seeds are per item, so results
do not depend on the device.
