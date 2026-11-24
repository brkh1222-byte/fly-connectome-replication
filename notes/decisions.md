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

## D6. Compute plan: laptop only (no H100)
(Filled in after benchmarking; see below.)
