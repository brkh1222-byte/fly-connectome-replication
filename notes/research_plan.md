<!-- Snapshot of the Claude Doc https://claude.ai/artifact/6CJ3Y75BL35HvfPL5JtfCx (exported 2026-11-24). The live doc is the source of truth. -->

# Fly Connectome Replication — Research Understanding & Plan

Nov 24, 2026

## Part A: What we're studying

**Bottom line:** no paper has yet asked whether the Shiu et al. (2024) whole-brain fly model gives the same answers on other flies' connectomes. But one experiment (sugar → MN9) has already been run informally on all three datasets, and BANC mostly failed it. The strongest study therefore asks how much of a failure comes from reconstruction quality rather than from real individual differences. It does this with a "variability ladder" and a synthetic "degraded FlyWire" control.

**How this was made:** AI-assisted research (Claude, with the academic-research-skills deep-research and academic-paper workflows). It builds on the reference checks in the [22 Nov plan doc](https://claude.ai/artifact/NUsQHxqic83YHj1GBnbsYY) and adds a search for new work on 24 Nov 2026. Several 2026 items are preprints or GitHub projects, not peer-reviewed papers. Open each one yourself before you cite it.

### A1. Core concepts

The project rests on one idea. If a brain's wiring diagram is enough to predict behaviour, the prediction should not depend on which fly's wiring diagram you use.

**Connectome.** A connectome is a map of every neuron and every synapse in a nervous system. To make one, scientists slice a brain into thousands of very thin sections and image each section with an electron microscope. AI then traces each neuron through the stack, and people check the result (this checking is called proofreading). The finished data are two tables: a neuron list (each neuron's cell type and predicted neurotransmitter) and a connection list (neuron A → neuron B, with the number of synapses between them).

**Why one connectome is a sample of one.** FlyWire is the brain of one adult female fly. Two connectomes can differ for three reasons that look the same in the data:

1. Real biological differences between individual flies.
2. Reconstruction differences: different imaging, AI tracing, proofreading and synapse detection.
3. Sex differences.

A good design pulls these three apart.

**Leaky integrate-and-fire (LIF) neuron.** This is the simplest model of a spiking neuron. Think of a leaky bucket. Excitatory inputs pour water in, inhibitory inputs take water out, and water slowly leaks away. When the level reaches a threshold, the neuron fires a spike. The bucket is then emptied to a reset level, and the neuron cannot fire again for a short refractory period. In Shiu's model, each neuron i has a membrane voltage v\_i and a synaptic input g\_i:

```latex
\tau_m \frac{dv_i}{dt} = g_i - (v_i - v_0), \qquad \tau_g \frac{dg_i}{dt} = -g_i, \qquad g_i \mathrel{+}= w_{ji} \text{ when neuron } j \text{ spikes}
```

The weight w\_ji is the synapse count from j to i, multiplied by one global constant W\_syn = 0.275 mV. It is then multiplied by +1 or −1 according to neuron j's predicted transmitter: acetylcholine is excitatory, while GABA and glutamate are treated as inhibitory. The other constants come from earlier fly recordings: resting and reset potential −52 mV, threshold −45 mV, τ\_m = 20 ms, τ\_g = 5 ms, refractory period 2.2 ms and synaptic delay 1.8 ms (from Shiu's code defaults).

**The Shiu et al. 2024 model.** Shiu and colleagues turned the FlyWire connectome (127,400 proofread neurons, materialization v630) into one LIF network and simulated it in Brian2 ([Shiu et al. 2024](https://doi.org/10.1038/s41586-024-07763-9)). Only one number was tuned: W\_syn, chosen so that 100 Hz input to the sugar-taste neurons drives the proboscis motor neuron MN9 to about 80% of its maximum. To run an experiment, they "stimulated" sensory neurons with random (Poisson) spike trains and recorded which neurons became active. They report 91% agreement across 164 predictions that could be tested in real flies. These include which neurons drive feeding (sugar → MN9) and antennal grooming.

**What "replication across individuals" means here.** We run the same code with the same constants on another fly's connectome, stimulate the same cell types, and ask two questions. Do the same downstream cell types turn on? Do they rank in the same order of strength? Neurons have no shared ID across datasets, so every comparison is made at the cell-type level. For example, the sugar-sensing gustatory receptor neurons (GRNs) form one type. This is why cell-type matching is a core step.

**Why two comparisons.** FlyWire and BANC are both female, so FlyWire vs BANC measures individual plus reconstruction differences. FlyWire vs the male CNS adds sex differences on top. A different lab reconstructed each dataset, so a raw comparison cannot separate these sources. The control experiments in Part B are designed to do that.

### A2. Key literature

The story has four steps. First, connectomes became possible (1986–2020). Second, whole fly brains were mapped and simulated (2024). Third, more individual flies were mapped (2026). Fourth, researchers began asking whether models built on one fly transfer to another (2025–2026).

| Year | Paper | What it found | Why it matters to us |
| --- | --- | --- | --- |
| **Foundations** |  |  |  |
| 2021 | [Witvliet et al., *Nature* 596:257](https://doi.org/10.1038/s41586-021-03778-8) | 8 *C. elegans* worms share a core wiring plan, but each also has its own extra connections. | First clear evidence that connectomes vary between individuals of one species. |
| 2020 | [Scheffer et al., *eLife* 9:e57443](https://doi.org/10.7554/eLife.57443) | The hemibrain: about half of one fly's central brain. | The first large fly connectome, and the dataset FlyWire was later compared with. |
| 2013 | [Bargmann & Marder, *Nat. Methods* 10:483](https://doi.org/10.1038/nmeth.2451) | Wiring alone does not fix function: neuromodulators, gap junctions and cell biophysics also matter. | The classic sceptical position that our results speak to. |
| 1986 | [White et al., *Phil. Trans. R. Soc. B* 314:1](https://doi.org/10.1098/rstb.1986.0056) | First complete connectome (*C. elegans*, 302 neurons). | Where connectomics began. |
| **The 2024 FlyWire package** |  |  |  |
| 2024 | [Dorkenwald et al., *Nature* 634:124](https://doi.org/10.1038/s41586-024-07558-y) | Complete adult female fly brain: 139,255 neurons and 54.5 million synapses. | Our reference connectome. |
| 2024 | [Schlegel et al., *Nature* 634:139](https://doi.org/10.1038/s41586-024-07686-5) | 8,453 cell types. FlyWire and the hemibrain are broadly stereotyped: edges with more than 10 synapses recur more than 90% of the time. Edge weights correlate at R = 0.97 between the two halves of one brain and R = 0.8 between brains. | Shows which edges are reliable, and that cell type is the right unit for matching. |
| 2024 | [Lin et al., *Nature* 634:153](https://doi.org/10.1038/s41586-024-07968-y) | Network statistics: a rich club, recurring motifs, and a few strong connections among many weak ones. | Structural baseline that describes what our null models keep. |
| 2024 | [Eckstein et al., *Cell* 187:2574](https://doi.org/10.1016/j.cell.2024.03.016) | Neurotransmitters predicted from EM images: 87% accurate per synapse, 94% per neuron. | Source of every excitatory or inhibitory sign in the model. |
| 2024 | [Shiu et al., *Nature* 634:210](https://doi.org/10.1038/s41586-024-07763-9) | Whole-brain LIF model; 91% of 164 testable predictions agreed with experiments (feeding, grooming). | The model we are replicating. |
| 2024 | [Pospisil et al., *Nature* 634:201](https://doi.org/10.1038/s41586-024-07982-0) | A linear "effectome" fitted to optogenetic experiments, using the connectome as a prior. The brain behaves like many small, nearly independent circuits. | Alternative to LIF. Suggests that local circuits such as taste → MN9 may be robust. |
| 2024 | [Lappalainen et al., *Nature* 634:1132](https://doi.org/10.1038/s41586-024-07939-3) | A connectome-constrained deep network predicts visual responses reported in 26 studies. | Connectome models can predict activity when the unknown parameters are fitted. |
| **More individuals** |  |  |  |
| 2026 | [Bates et al., *Nature* 656:957 (BANC)](https://doi.org/10.1038/s41586-026-10735-w) | A second female fly, brain plus nerve cord. Only 18% of synaptic links have an identified neuron on both sides, vs 41.9% for FlyWire. | Our second female. Its lower completeness is the main confound. |
| 2026 | [Berg et al., *Cell* 189:5504 (male CNS)](https://doi.org/10.1016/j.cell.2026.08.015) | A complete male CNS. Most cell types match the female. Sex-different types sit in higher brain centres; the sensory and motor periphery is largely the same. | Our male. It predicts that the taste and grooming circuits should be similar across the sexes. |
| 2026 | [Tastekin et al., *Cell* 189:5527](https://doi.org/10.1016/j.cell.2026.08.016) | Full taste connectome across the sexes. Taste-to-motor routes are largely shared, with some sex-specific biases. | Structural expectations for our sugar, bitter and water tests. |
| **Do models transfer? (2025–2026)** |  |  |  |
| 2026 | [Liu, arXiv:2611.14508](https://arxiv.org/abs/2611.14508) | Conclusions from real vs shuffled wiring can flip, depending on physiology that was never measured. | Warns us to test robustness across parameters, not just one setting. |
| 2026 | [Yad & Nabila, arXiv:2610.29205](https://arxiv.org/abs/2610.29205) | In the head-direction circuit, reconstruction differences are about as large as differences between flies. | The closest formal precedent for our question. |
| 2026 | [Minnick et al., arXiv:2610.33881](https://arxiv.org/abs/2610.33881) | Shiu's model run on BANC in a virtual body: sugar → MN9 is weak and water is silent. | Shiu's model is already partly ported to BANC. |
| 2025 | [Beiran & Litwin-Kumar, *Nat. Neurosci.* 28:2561](https://doi.org/10.1038/s41593-025-02080-4) | The connectome alone often does not fix a circuit's dynamics; recordings from a few neurons can. | Theory for why connectome simulations may or may not be robust. |

**How they connect.** The 2024 package made a whole-brain model possible, and Shiu showed that it predicts behaviour. BANC and the male CNS now provide more individual flies. The 2026 preprints show that differences between reconstructions can be as large as differences between flies. Our study sits at that last step, for the most-cited whole-brain model.

### A3. Open questions and debates

The central debate is how much of behaviour is "written in the wiring". Our project tests one sharp version of it.

- **Is the connectome enough?** Sceptics argue that neuromodulators, gap junctions and cell biophysics matter as much as wiring ([Bargmann & Marder 2013](https://doi.org/10.1038/nmeth.2451)). Shiu's 91% success is the strongest counter-example, but it comes from one fly. If the same model fails on another fly, the "wiring is enough" reading gets weaker.
- **Individual or reconstruction differences?** When two connectomes differ, is it biology or method? [Yad & Nabila](https://arxiv.org/abs/2610.29205) find that method differences can be nearly as large as fly-to-fly differences. BANC's lower linked-synapse fraction (18% vs 41.9%) makes this question especially sharp for us.
- **How should synapse counts become weights?** The options include raw counts, fraction of a neuron's input, or something else. Datasets detect synapses at different densities, so the choice changes the results. [brainlab](https://github.com/Pronexsteam/brainlab) showed that one fix restores MN9 but makes the whole brain about 12× more active. There is no agreed answer.
- **Are the transmitter signs right?** Per-neuron predictions are about 94% accurate, but a few wrong signs on key neurons can flip a pathway. Glutamate's sign is genuinely ambiguous in flies. Each connectome also has its own predictions.
- **Do sex differences matter for these circuits?** Male–female differences sit mostly in higher brain centres, while the taste and grooming periphery is largely shared ([Berg et al.](https://doi.org/10.1016/j.cell.2026.08.015); [Tastekin et al.](https://doi.org/10.1016/j.cell.2026.08.016)). So we expect small sex effects on Shiu's pathways, but nobody has simulated this.
- **What is the right null model?** Beating a randomly rewired network is easy. [Liu 2026](https://arxiv.org/abs/2611.14508) shows that real-vs-shuffled conclusions can flip with physiology that was never measured. So the result must also hold across parameter settings, not just against a shuffle.

### A4. Is our question still unanswered?

Yes, but narrowly. No peer-reviewed paper or formal preprint (searched 24 Nov 2026) runs Shiu's set of predictions across FlyWire, BANC and the male CNS, or uses the female–female vs female–male contrast. However, a GitHub project has already run the headline sugar → MN9 test on all three, and BANC mostly failed it. We must cite this project and clearly go beyond it.

| Work | What it did | Overlap with us |
| --- | --- | --- |
| [brainlab](https://github.com/Pronexsteam/brainlab) (GitHub, Sept 2026; see also [BANC issue #1](https://github.com/htem/BANC-project/issues/1)) | Ran Shiu's model unchanged on FlyWire v783, male CNS v0.9 and BANC v888. Sugar → MN9 rates were 76.7, 68.9 and 17.8 Hz. The same identified cells in BANC receive about 0.35× as many input synapses (MN9: 2,816 vs 8,021 in FlyWire). Per-type normalisation restores MN9 to 57.8 Hz but makes the whole brain about 12× more active. | **Near-scoop of one experiment.** Not a paper. One prediction only, no statistics, no left–right baseline, no sex contrast. |
| [Minnick et al. 2026, arXiv:2610.33881](https://arxiv.org/abs/2610.33881) | Shiu's model with untuned parameters on BANC (172,433 neurons) inside a simulated body. Sugar drives MN9 only weakly (1.9 Hz at 200 Hz input); water leaves MN9 silent. | Partial overlap: one connectome, no quantitative comparison with FlyWire or the male CNS. |
| [Yad & Nabila 2026, arXiv:2610.29205](https://arxiv.org/abs/2610.29205) | Head-direction circuit in 4 flies plus 5 versions of one fly. Changing only the synapse detector moves one fly's wiring 78–83% as far as the smallest between-fly difference. Trained models do not transfer across reconstructions. | Partial overlap: the best evidence that reconstruction differences can look like individual differences. One circuit, and not Shiu's model. |
| [Cho 2026, Zenodo preprint](https://doi.org/10.5281/zenodo.23678526) | Three "builds" of the same FlyWire v783 data under Shiu's model, scored on 37 tasks. The choice of build changes scores about as much as a change of model does. | Partial overlap: sensitivity to how one fly's data are processed. |
| [opifor/femaleflybrain](https://github.com/opifor/femaleflybrain) (GitHub, new on 24 Nov check) | Shared test bench that loads the male CNS, FlyWire and BANC, with pre-registered courtship experiments. Reports negative results, e.g. song input did not reach vpoDN. | Low overlap: courtship circuits, not Shiu's validated predictions. Worth citing as related tooling. |
| [indian-aman/drosophila-whole-cns-specificity](https://github.com/indian-aman/drosophila-whole-cns-specificity) (GitHub, new on 24 Nov check) | Whole-CNS simulations on the male CNS v1.0 and BANC v888: a virtual screen of 485 descending-neuron types and fru/dsx analyses *within* each connectome. | Low overlap: no cross-connectome replication of Shiu's predictions. |
| Hobby ports: [flymsg](https://github.com/gianlucamazza/flymsg), [drosophila-brain-mlx](https://github.com/Kisame76/drosophila-brain-mlx) | Run Shiu's model on the male CNS. flymsg divides W\_syn by 1.43 to correct for the male CNS's higher synapse density. | Background: shows that the density problem is already known. |

The repo claims above come from their READMEs (seen in search results on 24 Nov 2026) and have not been independently re-run.

**The real gap — what is left for us:**

1. A systematic replication of several Shiu predictions (sugar, bitter, water, grooming) on all three connectomes, with statistics.
2. A **variability ladder**: within one fly (FlyWire left vs right half), between two females (FlyWire vs BANC), and between sexes (vs male CNS). Nobody has measured simulation agreement at all three levels.
3. A pre-specified answer to the density and completeness problem: several normalisations compared, not one ad-hoc fix.
4. A test of whether simulation differences are explained by reconstruction completeness (BANC 18% vs FlyWire 41.9% linked synapses) rather than by individuality.

The field moves fast: 5+ related preprints and repos appeared between September and November 2026. A quick preprint matters.

### A5. Methods, datasets, tools and known pitfalls

The standard pipeline is:

1. Download the edge list and the neuron table.
2. Sign each neuron by its predicted transmitter.
3. Build a sparse weight matrix.
4. Drive chosen sensory neurons with Poisson spikes.
5. Read out firing rates over repeated trials.

The simulation is the easy part. The hard part is making three datasets comparable.

**Datasets**

| Dataset | Animal | Coverage | Size (as reported) | Access we use |
| --- | --- | --- | --- | --- |
| [FlyWire v783](https://zenodo.org/records/10676866) | 1 adult female | Brain only | 139,255 neurons, 54.5 M synapses | Zenodo + Shiu repo files |
| [BANC v888](https://doi.org/10.7910/DVN/7WTH1N) | 1 adult female | Brain + neck + nerve cord | 155,916 neurons (Nature version, v888) | Harvard Dataverse, no login for the edge list |
| [Male CNS v1.0](https://male-cns.janelia.org/download/) | 1 adult male | Brain + nerve cord | \~166k neurons ([Berg et al. 2026](https://doi.org/10.1016/j.cell.2026.08.015)) | Public Janelia GCS bucket |

**Tools**

- **Brian2:** the reference simulator Shiu used. It is slow, but it is the ground truth for validation.
- **PyTorch sparse LIF:** runs many trials at once (a sparse matrix times a batch of state vectors), which makes thousands of runs feasible on one H100. Reimplement it from the equations, because the eonsystemspbc port is GPL.
- **pandas / pyarrow** for the feather and parquet tables. Avoid fafbseg and CAVE-based tools: they call flywire.ai services.

**Known pitfalls and what we do about each**

| Pitfall | Why it matters | Fix |
| --- | --- | --- |
| Synapse density differs, but W\_syn is per synapse | W\_syn was tuned on FlyWire. BANC detects fewer synapses (\~0.35× input on matched cells), so it is underdriven. The male CNS detects more, so it is overdriven. | Compare several weight normalisations. Never re-tune W\_syn on the readout we are testing (sugar → MN9): that would be circular. |
| Brain-only vs whole CNS | FlyWire has no nerve cord. Extra loops through the cord in BANC and the male CNS can change brain activity. | Use a matched brain-only subgraph as the primary analysis and the whole CNS as secondary. |
| Transmitter signs are predictions | About 87% accurate per synapse and 94% per neuron ([Eckstein et al.](https://doi.org/10.1016/j.cell.2024.03.016)). Glutamate can excite or inhibit; Shiu found that treating it as excitatory raised false positives from 1% to 16%. | Add a control with one consensus sign per cell type across the three datasets. |
| Cell-type matching is incomplete | There are no shared IDs, and sensory types are often renamed, split or merged. | Report coverage. Compute every metric on the matched set only. |
| Absolute firing rates are unreliable | Shiu et al. say so themselves. | Use rank-based metrics: which types turn on, and in what order. |
| "> 0 Hz = activated" is fragile | One stray spike flips the label. | Use a rate threshold plus consistency across trials, and test several thresholds. |
| Weak nulls flatter any result | Shiu's shuffled networks almost never drive MN9 (1 of 100). | Add stronger controls: left vs right within one fly, and degraded FlyWire. |
| Version drift | Shiu used v630; we use v783. | Run Shiu's experiments on both versions as a small replication check. |
| Mixed data licences | Some FlyWire-derived annotation files are reported as CC BY-NC. | Check each file's licence before use. |

### A6. Citation audit of PROPOSAL.md

Every reference, repo and dataset in PROPOSAL.md exists; none is fabricated. However, three factual claims, one author order and one title need fixing, and one essential paper is missing. Items were checked against Crossref/doi.org, arXiv, bioRxiv, GitHub, Zenodo, Dataverse and GCS on 22 Nov 2026. Items 1, 5 and 6 were re-checked by search on 24 Nov 2026.

| # | As cited in PROPOSAL.md | Verdict | Correct citation / what to fix |
| --- | --- | --- | --- |
| 1 | Shiu et al. 2024, *Nature* 634:210 | **Citation OK, 2 claims wrong** | Shiu, P. K., Sterne, G. R., Spiller, N., Franconville, R., et al. (2024). A *Drosophila* computational brain model reveals sensorimotor processing. *Nature*, 634, 210–219. [doi:10.1038/s41586-024-07763-9](https://doi.org/10.1038/s41586-024-07763-9). **Fix:** the model used 127,400 neurons (v630), not \~140,000 (the v783 count). It has one tuned parameter, W\_syn = 0.275 mV, so "no free parameters" is wrong. |
| 2 | Dorkenwald et al. 2024, *Nature* (FlyWire) | Verified | Dorkenwald, S., Matsliah, A., Sterling, A. R., et al. (2024). Neuronal wiring diagram of an adult brain. *Nature*, 634, 124–138. [doi:10.1038/s41586-024-07558-y](https://doi.org/10.1038/s41586-024-07558-y). PROPOSAL.md gives no DOI; add it. |
| 3 | Schlegel et al. 2024, *Nature*, doi …7686-5 | **DOI OK, claim overstated** | Schlegel, P., Yin, Y., Bates, A. S., et al. (2024). Whole-brain annotation and multi-connectome cell typing of *Drosophila*. *Nature*, 634, 139–152. [doi:10.1038/s41586-024-07686-5](https://doi.org/10.1038/s41586-024-07686-5). **Fix:** the paper reports broad stereotypy (R = 0.97 within a brain, 0.8 across brains), not "edge weights vary substantially". |
| 4 | Lin et al. 2024, *Nature*, doi …7968-y | Verified | Lin, A., Yang, R., Dorkenwald, S., et al. (2024). Network statistics of the whole-brain connectome of *Drosophila*. *Nature*, 634, 153–165. [doi:10.1038/s41586-024-07968-y](https://doi.org/10.1038/s41586-024-07968-y) |
| 5 | Bates et al. 2026, BANC, *Nature*, doi …10735-w | Verified (re-checked) | Bates, A. S., Phelps, J. S., Kim, M., Yang, H. H., et al. (2026). Distributed control circuits across a brain-and-cord connectome. *Nature*, 656, 957–970. [doi:10.1038/s41586-026-10735-w](https://doi.org/10.1038/s41586-026-10735-w). Preprint: [doi:10.1101/2025.07.31.667571](https://doi.org/10.1101/2025.07.31.667571). Female fly. |
| 6 | Berg et al. 2026, male CNS, *Cell*, doi …2026.08.015 | **DOI OK, use the published title** | Berg, S., Beckett, I. R., Costa, M., Schlegel, P., et al. (2026). Sexual dimorphism in the complete connectome of the *Drosophila* male central nervous system. *Cell*, 189(18), 5504–5526. [doi:10.1016/j.cell.2026.08.015](https://doi.org/10.1016/j.cell.2026.08.015) ([PubMed 41279223](https://pubmed.ncbi.nlm.nih.gov/41279223/)). Some pages show a slightly different title word order; cite PubMed's. |
| 7 | Yad & Nabila 2026, arXiv:2610.29205 | Verified (preprint) | Yad, M. A. A., & Nabila, N. T. (2026). Reconstruction differences rival individual differences in the fly compass connectome and break trained circuit models. [arXiv:2610.29205](https://arxiv.org/abs/2610.29205). Not peer reviewed. |
| 8 | An 2026, bioRxiv 10.64898/2026.09.19.752860 | Verified (preprint) | An, D. (2026). How sparse can a fly-brain model be? [doi:10.64898/2026.09.19.752860](https://doi.org/10.64898/2026.09.19.752860). 10.64898 is bioRxiv's real 2026 DOI prefix. |
| 9 | Chen & Xi 2025, bioRxiv 10.64898/2025.12.14.694122 | **Author order wrong** | Xi, W., & Chen, W. (2025). Whole-brain connectomics of *Drosophila* reveals a robust, distributed architecture for the suppression of feeding during escape. [doi:10.64898/2025.12.14.694122](https://doi.org/10.64898/2025.12.14.694122). Checked via DOI on 22 Nov; open the DOI yourself before citing. |
| 10 | Asis 2026, arXiv:2611.09930 | Verified (preprint) | Asis, D. F. (2026). Specific, cumulative and reversible odour learning in a whole-brain connectome model of *Drosophila*. [arXiv:2611.09930](https://arxiv.org/abs/2611.09930) |
| 11 | GitHub: drosophila-brain-mlx, flymsg, eonsystemspbc/fly-brain | Verified | The first two are MIT-licensed ports of Shiu's model to the male CNS. eonsystemspbc/fly-brain is GPL-2.0-or-later; its README links to flywire.ai, so do not follow it. |
| 12 | Data: Zenodo 10676866; gs://flyem-male-cns/v1.0; Dataverse 7WTH1N | Verified | FlyWire v783 `proofread_connections_783.feather` (852 MB, CC BY 4.0). Male CNS `connectome-weights-male-cns-v1.0-minconf-0.5.feather` (1.05 GB, CC BY). BANC `banc_888_edgelist_simple_v2.feather` (305 MB) + `banc_888_meta.feather` + `banc_888_neurotransmitter_prediction_v2.csv`, no login. Only the raw `chunk_*.parquet` files are restricted, and we do not need them. |

**Missing and essential:** [Minnick et al. 2026, arXiv:2610.33881](https://arxiv.org/abs/2610.33881) and [brainlab](https://github.com/Pronexsteam/brainlab) (A4). Both already ran Shiu's model on BANC.

**Integrity note:** a citation being *verified* means it exists and says what we claim. You still need to open and read each paper before citing it in your own text.

## Part B: How we'll study it

### B1. Refined research question and hypotheses

**Research question:** When the Shiu et al. (2024) whole-brain LIF model is run unchanged on two other flies' connectomes, do its experimentally validated predictions replicate? And is any disagreement larger than (a) the disagreement between the two halves of one brain, and (b) the disagreement expected from reconstruction completeness alone?

This is sharper than the five questions in PROPOSAL.md. It puts the main confound, BANC's lower completeness, inside the question instead of hoping to read sex effects off raw comparisons.

**Hypotheses** (pre-registered before any cross-connectome run):

| ID | Hypothesis | Test | Supported if |
| --- | --- | --- | --- |
| H1 Replication | Four core Shiu predictions reproduce on BANC and the male CNS under the pre-specified primary normalisation: (1) sugar GRNs activate MN9; (2) bitter GRNs suppress sugar-evoked MN9; (3) water GRNs activate MN9; (4) JO-CE neurons activate the grooming neuron aBN1, while JO-F do not. | Per prediction: readout rate over 30 trials vs a no-stimulus control (one-sided Mann–Whitney). For bitter: sugar + bitter vs sugar alone. | At least 3 of 4 predictions reproduce in each connectome (Holm-corrected). |
| H2 Ladder | Agreement of whole-brain response profiles falls in order: within-fly (FlyWire left vs right) > FlyWire vs BANC > FlyWire vs male CNS. | Spearman ρ and top-k overlap over matched cell types, with bootstrap CIs. | Paired bootstrap differences between rungs exclude 0 in the predicted direction. |
| H3 Completeness | FlyWire–BANC disagreement is no larger than the disagreement between FlyWire and a copy of FlyWire degraded to BANC-like completeness. | Compare observed agreement with 20 degraded-FlyWire copies. | Observed value falls inside the degraded copies' 95% range. |
| H4 Robustness | The H1–H3 verdicts hold across weight normalisations, sign schemes, W\_syn ±30% and synapse threshold (0 vs 5). | Repeat the primary analyses on every setting. | The same qualitative verdict holds in at least 80% of settings. |

**Why H3 is the key idea.** H3 is what makes this study more than brainlab's single comparison. If H3 holds, BANC's differences are explained by reconstruction, and we cannot claim individual differences. If H3 fails, the remaining gap is a candidate for real individual or sex differences.

**Stress test of the argument** (the strongest objections, and our answers):

- *"BANC is just worse data, so of course it fails."* That is exactly what H3 tests, with a number instead of an assumption.
- *"n = 1 fly per dataset proves nothing about flies in general."* Agreed. The claims are about these three individuals, and the left–right rung gives a within-animal baseline.
- *"You tuned the model until it worked."* The primary normalisation is fixed and pre-registered, and W\_syn is never re-tuned on the readouts we test.

### B2. Study design and methods

The design is a computational replication built as a **variability ladder**. One fixed model is compared across network pairs ordered from "same brain" to "different sex". Synthetic controls show what pure reconstruction noise would do.

**Step 1 — Reproduce, then validate the GPU port (Gate 1).** Run Shiu's Brian2 code on FlyWire v630 (exactly as published) and on v783. Then build the PyTorch sparse LIF. It must match Brian2 in two ways. Per-neuron mean rates over 30 trials must correlate at r > 0.99. MN9 rates must fall within each other's 95% CI for three experiments: sugar, sugar + bitter, and JO-CE. *Why:* CLAUDE.md requires this, and every later result depends on a correct port.

**Step 2 — Standardise the three datasets.** Build one neurons table (id, cell type, side, superclass, transmitter, sign, region: brain, neck or nerve cord) and one edges table (pre, post, synapse count). Match cell types using BANC's built-in `fafb_783_match_id` column and the male CNS's FlyWire-matched type names. *Why:* published crosswalks give better coverage and more credibility than hand-matching.

**Step 3 — Measure how the datasets differ before simulating.** For each matched type, record input synapses per neuron, number of partners, and the fraction of inputs that come from identified neurons. *Why:* these numbers set the normalisation and the degraded-FlyWire control, and they make a figure of their own.

**Step 4 — Pre-register (Gate 2).** Post the hypotheses, primary settings, thresholds and metrics on OSF or Zenodo before Step 5. *Why:* related 2026 studies were pre-registered, so reviewers in this niche expect it. It also timestamps priority.

**Step 5 — Run the ladder.** Use the same stimuli (Poisson input at Shiu's rates) and 30 trials × 1 s on every network. Each rung adds one source of difference, so the gaps between rungs can be read:

| Comparison | Simulation noise | Reconstruction method | Different individual | Different sex | Expected agreement |
| --- | --- | --- | --- | --- | --- |
| FlyWire left vs right (and BANC left vs right) | yes | – | – | – | highest |
| FlyWire vs degraded FlyWire (20 copies) | yes | synthetic | – | – | high |
| FlyWire vs BANC | yes | yes | yes | – | ? (H2, H3) |
| FlyWire or BANC vs male CNS | yes | yes | yes | yes | ? (H2) |
| FlyWire vs degree-preserving shuffle | yes | wiring destroyed | – | – | lowest |

*Degraded FlyWire* = FlyWire with synapses removed at random until each matched type's input count matches BANC's.

**Step 6 — Primary settings (fixed in advance).**

- **Network:** a brain-only subgraph in every dataset, so all three cover the same tissue. Whole-CNS runs are secondary.
- **Weights:** N1, global density scaling. W\_syn per dataset = 0.275 mV × (FlyWire median input synapses per matched neuron ÷ that dataset's median). The median is taken over all matched neurons except the readout neurons. This gives one number per dataset, never tuned on the outcome. Secondary: N0, raw counts (Shiu's rule), and N2, fraction-of-input weights.
- **Signs:** each dataset's own transmitter predictions (primary); one consensus sign per cell type (secondary).
- **Threshold:** all synapses, as Shiu used (primary); at least 5 synapses (secondary).

**Step 7 — Stimulation screen (stretch goal).** Stimulate every matched sensory type and compare full response profiles across connectomes. Only if Weeks 1–3 finish on time.

**Why this design:**

- It reuses Shiu's own experiments, so "replicate" has a clear meaning.
- It adds the two controls that earlier attempts lacked: a within-fly baseline and a completeness-matched degradation.
- It fixes every analysis choice before any cross-connectome result is seen.

### B3. Analysis plan: statistics and controls

Every metric works at the cell-type level and on ranks. Neurons have no shared IDs across datasets, and Shiu et al. warn that absolute rates are unreliable.

**Metrics**

- **Prediction replicated (H1).** The readout neuron's 30 trial rates must beat a no-stimulus control (one-sided Mann–Whitney) and reach at least 20% of the FlyWire rate at the same input. For bitter, sugar + bitter must be lower than sugar alone. That gives 4 predictions × 2 connectomes = 8 primary tests, Holm-corrected at α = 0.05.
- **Profile agreement (H2, H3).** Average the rate of all neurons in a matched type (same side) and take log(1 + rate). Compute Spearman ρ over all types active (≥ 1 Hz) in either network. Also compute top-k overlap (Jaccard index) for k = 20 and k = 50.
- **Uncertainty.** Draw 1,000 bootstrap resamples over trials and over matched cell types, and report 95% percentile CIs. Ordering claims in H2 use paired bootstrap differences between rungs.
- **Seeds.** Fix and record every random seed, so any run can be repeated exactly.

**Controls**

| Control | What it rules out |
| --- | --- |
| PyTorch vs Brian2 | A bug in our simulator |
| FlyWire v630 vs v783 | Results that depend on the proofreading version |
| FlyWire left vs right; BANC left vs right | Mistaking ordinary within-fly variation for between-fly differences |
| Degraded FlyWire (×20) | Mistaking reconstruction incompleteness for individuality (H3) |
| Degree-preserving shuffle | "Any network would do this" (lower bound) |
| Normalisation, sign, W\_syn ±30% and threshold sweeps | Results that are an artefact of one modelling choice (H4) |

**Honest limit.** Each dataset is one animal. Confidence intervals describe simulation noise and cell-type sampling, not variation across the fly population. The paper must say "these three individuals", never "flies in general". The sex comparison is one male vs two females.

### B4. What counts as a positive, negative or null result

The analysis is pre-registered, so every outcome can be reported without p-hacking. That is what makes all four outcomes below publishable.

| Outcome | Pattern | What it means | Why it is publishable |
| --- | --- | --- | --- |
| Positive | H1 holds in both connectomes, and agreement is close to the left–right baseline. | Shiu's predictions belong to the fly's wiring plan, not to one animal. | Strong support for single-connectome modelling, and a clean replication of a high-profile *Nature* model. |
| Negative | Predictions fail on BANC or the male CNS even after normalisation, and BANC differs more than degraded FlyWire does (H3 fails). | Some predictions depend on individual wiring. | A cautionary result for the field. Replication-friendly journals explicitly welcome it. |
| Null / confounded | Failures occur, but degraded FlyWire explains them fully (H3 holds). | Current reconstructions are not complete enough to test individuality. | A quantitative completeness benchmark that tells connectome builders what is needed. This has methods value. |
| Mixed (most likely) | Sugar and bitter replicate; water or grooming fail; results depend on normalisation. | Robustness differs by pathway. | A map of which predictions modellers can trust. Directly useful to them. |

### B5. Paper structure, figures and target journal

**Target: [Royal Society Open Science](https://royalsociety.org/journals/open-access/open-science/).** It has a formal replication policy, publishes negative and null results, and offers Registered Reports. Alternatives: *PLOS Computational Biology* if the result is strongly positive, or mixed with a clear mechanism; *eNeuro*. Post a bioRxiv preprint first. Check bioRxiv's rules for authors under 18, and have the mentor co-submit if needed. [ReScience C](https://resciencec.theoj.org/about) is not a fit: it publishes pure reproductions, and this study goes further.

**Working title:** *Do whole-brain connectome simulations of* Drosophila *transfer between individuals? Testing the Shiu et al. model on three connectomes.*

| Section | Contents | Length |
| --- | --- | --- |
| Abstract | Question; design (ladder + degraded control); main numbers; one-line verdict | 250 words |
| Introduction | Connectome models; Shiu's success on one fly; individual vs reconstruction variability; the gap (A4); hypotheses | \~800 words |
| Methods | Data and versions; standardisation; matching; LIF model and GPU port; validation; normalisations; ladder; degraded-FlyWire control; metrics and statistics; pre-registration link | \~1,500 words |
| Results | (1) Port validated; (2) datasets differ in density and completeness; (3) replication of the 4 predictions; (4) agreement ladder; (5) completeness control; (6) robustness | \~1,800 words |
| Discussion | What replicates; reconstruction vs individuality; implications for connectome modelling; limitations (one animal per dataset, no gap junctions or neuromodulation, predicted signs); future work | \~1,000 words |
| Statements | Data and code availability; ethics (no human or animal subjects; public CC BY data); author contributions (CRediT); conflicts of interest; funding; AI-use disclosure | short |

**Figures**

1. **Design.** The three connectomes, the variability ladder and the controls.
2. **Validation.** PyTorch vs Brian2 rates (scatter of all neurons); v630 vs v783.
3. **The datasets differ.** Input synapses per matched type (FlyWire vs BANC vs male CNS), linked-synapse fraction, and the effect of each normalisation on mean activity.
4. **Replication.** 4 predictions × 3 connectomes × 3 normalisations: readout rate with CIs.
5. **Agreement ladder (key figure).** Spearman ρ and top-k overlap for every comparison, drawn over the degraded-FlyWire and shuffle distributions.
6. **Robustness.** The verdict for each setting in the sweep: signs, W\_syn, threshold, brain-only vs whole CNS.

Supplementary material: matching coverage table, stimulation screen (if done), full parameter list.

**Writing rule:** you write all the paper text yourself. Claude can explain methods, check numbers and comment on drafts.

### B6. Timeline and main risks

Four weeks is realistic only because two gates stop wasted work. If Gate 1 slips, everything shifts, but nothing built on a broken simulator has to be redone.

&#91;embedded content: four-week plan · 2 gates, preprint 22 Dec 2026\]

Write the Methods during Weeks 1–3, as each step is done, so Week 4 is mostly Results and Discussion.

**If only 2 weeks are available:** cut to FlyWire vs BANC, sugar and bitter only, normalisations N0 and N1, and the degraded-FlyWire control. That is still a complete, publishable test of H1 and H3.

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Someone posts the same study first (5+ related preprints and repos in Sept–Nov 2026) | High | High | Pre-register in Week 2 (this timestamps priority) and post the preprint by 22 Dec. The ladder and the degraded-FlyWire control set this apart from brainlab. |
| PyTorch port does not match Brian2 | Medium | High | Debug against Brian2 on a small subnetwork first. Fall back to Brian2 on CPU for the 4 core predictions: slow, but feasible. |
| Key types (GRNs, MN9, aBN1, JO-CE) missing or split in BANC or the male CNS | Medium | High | Check these types first in Week 2 and report coverage. Match via `fafb_783_match_id`, and by hand for the few that fail. |
| BANC too incomplete for any normalisation to help | Medium | Medium | This is itself a result (the null/confounded outcome in B4). The degraded-FlyWire control measures it. |
| Normalisations disagree with each other | High | Medium | Pre-specify N1 as primary and report all of them. H4 is about robustness, not one number. |
| Data licence or access surprise | Low | Medium | Zenodo, Dataverse and the Janelia bucket are CC BY and need no login. Never use flywire.ai, Codex or CAVE. |
| GPL contamination from eonsystemspbc/fly-brain | Low | Medium | Do not open its code. Reimplement from Shiu's equations and keep the repo MIT. |
| Writing is not finished in Week 4 | Medium | Medium | Write Methods as you go. The preprint can slip to early January without harm if it is pre-registered. |

## Suggested changes to PROPOSAL.md / TASKS.md

**PROPOSAL.md**

- [ ] **§1 Summary:** change "\~140,000 neurons" to "127,400 neurons (FlyWire v630)". Change "no free parameters fitted to behaviour" to "one free parameter (W\_syn = 0.275 mV), tuned to MN9 output".
- [ ] **§2 Background:** replace "edge weights vary substantially" with Schlegel's numbers: broad stereotypy; R = 0.97 within a brain and 0.8 across brains; edges with more than 10 synapses found again more than 90% of the time.
- [ ] **§3 Prior work:** add brainlab (sugar → MN9 on all three: 76.7 / 68.9 / 17.8 Hz), Minnick et al. 2026, Cho 2026 and Tastekin et al. 2026. Mention opifor/femaleflybrain and indian-aman/drosophila-whole-cns-specificity as related tooling. Fix "Chen & Xi" to "Xi & Chen". Rewrite the gap as the four points in A4.
- [ ] **§4 Questions:** replace the five questions with the RQ and H1–H4 (B1). Present the sex comparison as secondary and confounded, not as a headline.
- [ ] **§5 Data:** record the verified BANC files (`banc_888_edgelist_simple_v2.feather`, `banc_888_meta.feather`, `banc_888_neurotransmitter_prediction_v2.csv`, no login) and the male CNS weights file. Note BANC's 18% vs FlyWire's 41.9% linked-synapse fraction.
- [ ] **§6 Method:** add brain-only as the primary analysis; normalisations N0/N1/N2 with N1 primary; left–right baselines; the degraded-FlyWire control; numeric validation criteria; and a pre-registration step. Treat the degree-preserving shuffle as the lower bound of the ladder, not as "the null".
- [ ] **§7 Timeline:** use the gated plan in B6 (Gate 1 on 1 Dec, Gate 2 on 8 Dec, preprint by 22 Dec).
- [ ] **§8 Venues:** Royal Society Open Science first; PLOS Computational Biology or eNeuro as alternatives.
- [ ] **§9 Risks:** update the scoop risk (brainlab already ran one experiment) and add BANC completeness as the top scientific risk.
- [ ] **§10 References:** replace with the full citations in A2 and A6, using the published Berg et al. title. Remove the "compiled by an AI" warning only after you have opened each reference yourself.

**TASKS.md**

- [ ] **T0.2:** decide on MIT now, and do not open the eonsystemspbc/fly-brain code at all.
- [ ] **T1.3:** the file list and "no login needed" are already known. Only the raw `chunk_*.parquet` files are restricted, and we do not need them.
- [ ] **T1.4:** add a region column (brain / neck / nerve cord) and the cross-dataset match columns. Add per-type input synapses and linked-synapse fraction to `dataset_summary.csv`.
- [ ] **T2.1:** run Shiu's model on both v630 and v783.
- [ ] **T2.2:** make "done" numeric: per-neuron rate correlation r > 0.99 vs Brian2, and overlapping MN9 95% CIs on 3 experiments.
- [ ] **New T2.3 (Gate 2):** write and post the pre-registration (hypotheses, N1 primary, metrics, thresholds) before T3.2.
- [ ] **T3.1:** start by checking the critical types (sugar, bitter and water GRNs; MN9; aBN1; JO-CE and JO-F) in all three datasets, using BANC's `fafb_783_match_id`.
- [ ] **New T3.4:** left-only vs right-only stimulation in FlyWire and BANC (the within-fly baseline).
- [ ] **New T4.2b:** `src/degrade.py`, which builds 20 FlyWire copies with synapses removed to match BANC's per-type input counts.
- [ ] **T4.1:** list the exact sweep: N0/N1/N2 × own/consensus signs × W\_syn ±30% × threshold 0/5 × brain-only/whole CNS.
- [ ] **T4.3:** mark the full stimulation screen as a stretch goal.
- [ ] **T5.1:** add the required statements (data and code availability, ethics, CRediT, conflicts, funding, AI use) and the preprint step.

## Sources

The pages below were opened directly, or through their DOI or Crossref record, on 22 Nov 2026. New items and re-checks from 24 Nov 2026 come from search results only. Paper citations are in the A2 and A6 tables.

- Shiu et al. 2024 full text: [PMC11446845](https://pmc.ncbi.nlm.nih.gov/articles/PMC11446845/); code: [philshiu/Drosophila\_brain\_model](https://github.com/philshiu/Drosophila_brain_model)
- FlyWire v783 data: [Zenodo 10676866](https://zenodo.org/records/10676866)
- BANC data: [Harvard Dataverse 7WTH1N](https://doi.org/10.7910/DVN/7WTH1N); project: [htem/BANC-project](https://github.com/htem/BANC-project)
- Male CNS data: [male-cns.janelia.org/download](https://male-cns.janelia.org/download/); paper record: [PubMed 41279223](https://pubmed.ncbi.nlm.nih.gov/41279223/)
- Prior work: [brainlab](https://github.com/Pronexsteam/brainlab), [BANC issue #1](https://github.com/htem/BANC-project/issues/1), [Minnick et al.](https://arxiv.org/abs/2610.33881), [Yad & Nabila](https://arxiv.org/abs/2610.29205), [Cho](https://doi.org/10.5281/zenodo.23678526), [Liu](https://arxiv.org/abs/2611.14508)
- New on 24 Nov (search results): [opifor/femaleflybrain](https://github.com/opifor/femaleflybrain), [indian-aman/drosophila-whole-cns-specificity](https://github.com/indian-aman/drosophila-whole-cns-specificity)
- Follow-ups cited in PROPOSAL.md: [Asis](https://arxiv.org/abs/2611.09930), [An](https://doi.org/10.64898/2026.09.19.752860), [Xi & Chen](https://doi.org/10.64898/2025.12.14.694122)
- Hobby ports: [flymsg](https://github.com/gianlucamazza/flymsg), [drosophila-brain-mlx](https://github.com/Kisame76/drosophila-brain-mlx), [eonsystemspbc/fly-brain](https://github.com/eonsystemspbc/fly-brain) (GPL; do not reuse its code)
- Journals: [Royal Society Open Science](https://royalsociety.org/journals/open-access/open-science/), [ReScience C](https://resciencec.theoj.org/about)
