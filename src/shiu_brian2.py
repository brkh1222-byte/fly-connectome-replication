"""Reference Brian2 implementation of the Shiu et al. (2024) whole-brain LIF model.

This follows model.py of github.com/philshiu/Drosophila_brain_model (MIT, (c) 2023 Philip Shiu
and Nico Spiller; commit 91bdd1e) line for line in its equations, parameters, Poisson drive
and silencing. One engineering difference: Shiu rebuilds the network for every trial. Here the
network is built once, stored, and restored before each trial with a fresh seed. The dynamics
are identical; only wall-clock time changes.

Output: a parquet of spike counts (trial, idx, n) for every neuron that fired, plus a JSON
with the metadata. Neuron indices are rows of the completeness table (Shiu's "Brian ID").

Example:
  python src/shiu_brian2.py --version 783 --exp sugarR --rate 100 --trials 30 --seed 1 \
      --out results/brian2/sugarR_100Hz_783
"""
import argparse, json, sys, time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from experiments_def import SHIU_SETS  # noqa: E402

from paths import SHIU as SHIU_DIR  # noqa: E402
PATHS = {
    "630": (SHIU_DIR / "2023_03_23_completeness_630_final.csv",
            SHIU_DIR / "2023_03_23_connectivity_630_final.parquet"),
    "783": (SHIU_DIR / "Completeness_783.csv", SHIU_DIR / "Connectivity_783.parquet"),
}


def build(version, exc, exc2, slnc, rate, rate2, params, codegen="cython"):
    from brian2 import (NeuronGroup, Synapses, PoissonInput, SpikeMonitor, Network, prefs,
                        mV, ms, Hz)
    prefs.codegen.target = codegen
    path_comp, path_con = PATHS[version]
    df_comp = pd.read_csv(path_comp, index_col=0)
    df_con = pd.read_parquet(path_con, columns=["Presynaptic_Index", "Postsynaptic_Index",
                                                "Excitatory x Connectivity"])
    neu = NeuronGroup(N=len(df_comp), model=params["eqs"], method="linear",
                      threshold=params["eq_th"], reset=params["eq_rst"], refractory="rfc",
                      name="default_neurons", namespace=params)
    neu.v = params["v_0"]
    neu.g = 0
    neu.rfc = params["t_rfc"]
    syn = Synapses(neu, neu, "w : volt", on_pre="g += w", delay=params["t_dly"],
                   name="default_synapses")
    syn.connect(i=df_con["Presynaptic_Index"].values, j=df_con["Postsynaptic_Index"].values)
    w = df_con["Excitatory x Connectivity"].values.astype(float)
    if slnc:  # Shiu: silencing sets all outgoing weights of the silenced neuron to 0
        w[np.isin(df_con["Presynaptic_Index"].values, slnc)] = 0.0
    syn.w = w * params["w_syn"]
    pois = []
    for idxs, r in ((exc, rate), (exc2, rate2)):
        for i in idxs:
            pois.append(PoissonInput(target=neu[i], target_var="v", N=1, rate=r * Hz,
                                     weight=params["w_syn"] * params["f_poi"]))
            neu[i].rfc = 0 * ms
    mon = SpikeMonitor(neu, record=False)  # counts only
    net = Network(neu, syn, mon, *pois)
    return net, mon, df_comp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="783", choices=["630", "783"])
    ap.add_argument("--exp", required=True, help="key in experiments_def.SHIU_SETS")
    ap.add_argument("--exp2", default=None)
    ap.add_argument("--rate", type=float, default=150.0)
    ap.add_argument("--rate2", type=float, default=0.0)
    ap.add_argument("--silence", default="", help="comma-separated root ids")
    ap.add_argument("--trials", type=int, default=30)
    ap.add_argument("--t_run", type=float, default=1000.0, help="ms")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--codegen", default="cython")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    sys.path.insert(0, str(SHIU_DIR))
    from model import default_params  # Shiu's parameters, unchanged
    from brian2 import ms, seed as b2seed
    params = dict(default_params)

    df_comp = pd.read_csv(PATHS[a.version][0], index_col=0)
    id2i = {j: i for i, j in enumerate(df_comp.index)}
    def idx(name):
        if not name:
            return []
        ids = SHIU_SETS[name]
        found = [id2i[i] for i in ids if i in id2i]
        print(f"  {name}: {len(found)}/{len(ids)} ids present in v{a.version}")
        return found
    exc, exc2 = idx(a.exp), idx(a.exp2)
    slnc = [id2i[int(s)] for s in a.silence.split(",") if s and int(s) in id2i]

    t0 = time.time()
    net, mon, _ = build(a.version, exc, exc2, slnc, a.rate, a.rate2, params, a.codegen)
    net.store("init")
    t_build = time.time() - t0
    rows, t_trials = [], []
    for k in range(a.trials):
        net.restore("init")
        b2seed(a.seed * 100003 + k)
        t1 = time.time()
        net.run(a.t_run * ms)
        t_trials.append(time.time() - t1)
        cnt = np.asarray(mon.count[:])
        nz = np.nonzero(cnt)[0]
        rows.append(pd.DataFrame({"trial": k, "idx": nz.astype(np.int32),
                                  "n": cnt[nz].astype(np.int32)}))
        print(f"  trial {k}: {t_trials[-1]:.1f}s, {len(nz)} active, {cnt.sum()} spikes",
              flush=True)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.concat(rows).to_parquet(str(out) + ".parquet")
    meta = dict(vars(a), n_neurons=len(df_comp), n_exc=len(exc), n_exc2=len(exc2),
                t_build_s=t_build, t_trial_s=t_trials, simulator="brian2")
    json.dump(meta, open(str(out) + ".json", "w"), indent=1)
    print(f"done: build {t_build:.0f}s, mean trial {np.mean(t_trials):.1f}s")


if __name__ == "__main__":
    main()
