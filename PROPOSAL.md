# Research Proposal

## Do Whole-Brain Connectome Simulations Replicate Across Individual Flies? Testing the Shiu et al. Drosophila Model on FlyWire, BANC and the Male CNS

**Author:** Berkh (independent student researcher)
**Adult mentor / co-author:** [to be confirmed]
**Field:** Computational neuroscience / connectomics
**Planned duration:** 4 weeks
**Compute:** 1× NVIDIA H100 (80 GB)
**Status:** Proposal, Nov 2026

---

## 1. Summary

Shiu et al. (2024, *Nature* 634:210) built a **leaky integrate-and-fire (LIF) model of the entire adult *Drosophila* brain** directly from the FlyWire connectome (~140,000 neurons, ~50 million synapses). It contains no free parameters fitted to behaviour. Yet it correctly predicted which neurons drive feeding (sugar receptor neurons → motor neuron MN9) and grooming, and several predictions were confirmed experimentally.

All of this rests on **one fly's wiring diagram**. Two more whole-CNS connectomes are now public:
- **BANC** (brain and nerve cord, female; Bates et al. 2026, *Nature*)
- the **male CNS** (Berg et al. 2026, *Cell*)

**Question:** Do the model's predictions hold when the same simulation runs on a different individual's connectome? The **FlyWire vs BANC** comparison (both female) isolates individual and reconstruction differences. The **FlyWire vs male CNS** comparison adds sex differences. The H100 makes it possible to sweep tens of thousands of simulations: 3 connectomes × weight normalisations × synapse thresholds × edge-noise bootstraps × all sensory inputs.

## 2. Background

- **Connectome-constrained models** test how much behaviour follows from wiring alone. Shiu et al. used FlyWire v630 with neurotransmitter-predicted signs (excitatory/inhibitory). Their code is public (MIT licence) and supports v783.
- **Individual variability:** FlyWire's left and right hemispheres and the hemibrain differ in connection counts. Schlegel et al. 2024 (*Nature*) report that cell-type-level connectivity is largely stereotyped, but edge weights vary substantially. Whether *dynamical predictions* survive this variability is untested at whole-brain scale.

## 3. Prior work and the gap

| Work | What it did | Gap |
|---|---|---|
| Shiu et al. 2024, *Nature* 634:210; code github.com/philshiu/Drosophila_brain_model | Whole-brain LIF model on FlyWire; feeding and grooming predictions | One connectome |
| An 2026 (bioRxiv 10.64898/2026.09.19.752860); Chen & Xi 2025 (bioRxiv 10.64898/2025.12.14.694122); Asis 2026 (arXiv:2611.09930) | Follow-ups: sparsification, escape vs feeding, odour learning | All FlyWire only |
| Yad & Nabila 2026 (arXiv:2610.29205) | Head-direction circuit across male CNS, hemibrain, FlyWire, BANC; reconstruction differences rival individual differences | One circuit only; no whole-brain LIF predictions |
| Hobbyist ports (github: Kisame76/drosophila-brain-mlx, gianlucamazza/flymsg) | Ported the model to the male CNS | Not papers; note that sex cannot be separated from reconstruction differences without a second female |
| Lin et al. 2024; Schlegel et al. 2024 (*Nature*) | Rich-club, motifs, left/right and cross-dataset cell typing | Static structure, not simulation |

**Gap:** No systematic test exists of whether Shiu's validated whole-brain predictions replicate on BANC and the male CNS. No study uses the female–female comparison to separate individual variability from sex.

## 4. Research questions

1. **Replication:** Do sugar-GRN stimulation → MN9 activation, water, bitter and grooming pathways reproduce on BANC and the male CNS, in which neurons activate and at what rates?
2. **Agreement:** How well do the per-neuron firing rates agree across connectomes for matched cell types, measured by rank correlation and by overlap of the top-k activated neurons?
3. **Individual vs sex:** Is FlyWire–BANC agreement higher than FlyWire–male CNS agreement?
4. **Robustness:** Which modelling choices change the answers? Candidates are weight normalisation (raw counts, per-dataset density, fraction of inputs), the synapse-count threshold, and neurotransmitter-sign predictions.
5. **Null:** Is cross-connectome agreement higher than for degree-preserving shuffled connectomes?

## 5. Data (all CC BY 4.0)

| Dataset | Access | Notes |
|---|---|---|
| **FlyWire v783** | Zenodo 10.5281/zenodo.10676866 (connections ~852 MB) + Shiu repo files | Use Zenodo, **not** flywire.ai. The flywire.ai terms require a parent or guardian to agree for users under 18. |
| **Male CNS v1.0** | `gs://flyem-male-cns/v1.0/...` (weights ~1.1 GB, annotations, neurotransmitters); male-cns.janelia.org/download | Bulk bucket; neuPrint not needed |
| **BANC v888** | Harvard Dataverse doi:10.7910/DVN/7WTH1N | File sizes and login requirement unverified (T1.3) |
| Cross-dataset cell-type matches | Dataset annotations; taste-neuron types (e.g. LB3b/LB3c ↔ Gr64f sugar) | Build a matching table |

## 6. Method

1. **Reproduce:** run Shiu's Brian2 model on FlyWire v783 and reproduce sugar→MN9.
2. **GPU port:** use or adapt a PyTorch implementation (sparse matrix × batched state vectors; trials as columns). Validate that spike rates match Brian2 within seed noise. An existing GPU port (github.com/eonsystemspbc/fly-brain) is GPL-2.0+: if code is reused, this repo must be GPL-compatible. Otherwise reimplement from the paper equations.
3. **Load BANC and the male CNS** into the same format:
   - neuron table with type, side and neurotransmitter;
   - edge list with synapse counts;
   - sign from the predicted neurotransmitter.
4. **Matching:** match neurons across datasets by cell type, with side where possible. Run Shiu's stimulation experiments on each.
5. **Sweeps (H100):** normalisation × threshold × edge-noise bootstrap × seeds × all matched sensory types (a stimulation screen).
6. **Metrics:** replication of each prediction; rank correlation of firing rates over matched types; top-k overlap; comparison with degree-preserving shuffled nulls.

## 7. Timeline

| Week | Tasks |
|---|---|
| 1 | Reproduce Shiu on v783; GPU port and validation; download BANC and the male CNS |
| 2 | Cell-type matching tables; run Shiu's experiments on all three |
| 3 | Robustness sweeps and nulls on the H100; figures |
| 4 | Write-up; bioRxiv preprint |

## 8. Venues

- PLOS Computational Biology, eNeuro, or Royal Society Open Science (welcomes replications).
- JEI as the student alternative (needs an adult mentor).
- bioRxiv preprint: check bioRxiv's policy on minors and affiliation, and have the mentor co-submit if needed.

## 9. Risks

| Risk | Mitigation |
|---|---|
| Fast-moving field (≥4 related preprints Sept–Nov 2026) | Post a preprint by week 4; narrow, crisp question |
| Incomplete cell-type matching | Report coverage; analyse matched subsets |
| BANC sensory neurons truncated | Check per-pathway completeness; report it |
| Neurotransmitter predictions differ by dataset | Sensitivity analysis with swapped and consensus signs |
| GPL licence of the existing GPU port | Reimplement, or license this repo GPL-compatible |

## 10. Key references

- Shiu, P. K. et al. (2024). A Drosophila computational brain model reveals sensorimotor processing. *Nature* 634, 210
- Dorkenwald, S. et al. (2024). Neuronal wiring diagram of an adult brain. *Nature* (FlyWire)
- Schlegel, P. et al. (2024). *Nature*. doi:10.1038/s41586-024-07686-5
- Lin, A. et al. (2024). *Nature*. doi:10.1038/s41586-024-07968-y
- Bates, A. S. et al. (2026). BANC. *Nature*. doi:10.1038/s41586-026-10735-w
- Berg, S. et al. (2026). Male CNS connectome. *Cell*. doi:10.1016/j.cell.2026.08.015
- Yad & Nabila (2026). arXiv:2610.29205

> ⚠️ These references were compiled by an AI research assistant. Verify every citation and DOI before using it.
