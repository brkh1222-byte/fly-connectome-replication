"""T4.1-T4.3: the full grid, run in priority order with a resumable ledger.

Phases (each item = one connectome variant x one battery, 30 trials x 1 s per experiment):
  P1 nulls      T4.2  degraded FlyWire (to BANC and to male CNS deficits) x {N0, N1} x 50 copies
                      degree-preserving shuffles x 3 datasets x {N0, N1} x 50
  P2 sweep      T4.1  3 datasets x subgraph (brain; +cns for BANC/male CNS) x threshold {1,3,5,10}
                      x norm {N0,N1,N2} x sign {own, nt, type}  (base networks, core + core_rep)
                      + edge-noise bootstrap (Poisson-resampled synapse counts) x 10 for every
                      setting with sign 'own'
  P3 screen     T4.3  stimulation screen: every shared sensory type x side, 3 datasets x {N0, N1}
                      (+ shuffled controls x 5 per dataset under N1)

Usage:
  python src/sweep.py --list                        # print counts and planned items
  python src/sweep.py --device cuda [--phase P1]    # run (skips anything already in results/runs)
  python src/sweep.py --device cpu --tiny           # runbook self-test: 2 trials x 50 ms, 1 item/phase
"""
from __future__ import annotations

import argparse, itertools, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import connectome as C  # noqa: E402
import experiments as X  # noqa: E402

DS = C.DATASETS
THRESH = (1, 3, 5, 10)
NORMS = ("N0", "N1", "N2")
SIGNS = ("own", "nt", "type")
N_DEGRADE, N_SHUFFLE, N_EDGENOISE, N_SCREEN_SHUFFLE = 50, 50, 10, 5


def items(phase):
    out = []
    if phase == "P1":
        for ref in ("banc", "malecns"):
            for nm in ("N0", "N1"):
                for s in range(N_DEGRADE):
                    out.append((dict(dataset="flywire", norm=nm,
                                     perturb=dict(kind="degrade", seed=s, ref=ref)), "core"))
        for d in DS:
            for nm in ("N0", "N1"):
                for s in range(N_SHUFFLE):
                    out.append((dict(dataset=d, norm=nm, perturb=dict(kind="shuffle", seed=s)), "core"))
        for d in DS:  # D10: side-balanced stimulation for the hemisphere rung
            for nm in ("N0", "N1"):
                out.append((dict(dataset=d, norm=nm), "core_bal"))
    elif phase == "P2":
        for d in DS:
            subs = ("brain",) if d == "flywire" else ("brain", "cns")
            for sub, t, nm, sg in itertools.product(subs, THRESH, NORMS, SIGNS):
                base = dict(dataset=d, subgraph=sub, threshold=t, norm=nm, sign=sg)
                out.append((base, "core"))
                out.append((base, "core_rep"))
                if sg == "own":
                    for s in range(N_EDGENOISE):
                        out.append((dict(base, perturb=dict(kind="edgenoise", seed=s)), "core"))
    elif phase == "P3":
        for d in DS:
            for nm in ("N0", "N1"):
                out.append((dict(dataset=d, norm=nm), "screen"))
            for s in range(N_SCREEN_SHUFFLE):
                out.append((dict(dataset=d, norm="N1", perturb=dict(kind="shuffle", seed=s)), "screen"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--phase", default="P1,P2,P3")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--tiny", action="store_true")
    ap.add_argument("--max_rows", type=int, default=0, help="0 = auto from free GPU memory")
    a = ap.parse_args()
    phases = a.phase.split(",")
    for ph in phases:
        its = items(ph)
        if a.list:
            n_exp = {"core": 12, "core_rep": 12, "core_bal": 10, "screen": 2 * len(X.screen_types())}
            ts = sum(n_exp[b] * 30 for _, b in its)
            print(f"{ph}: {len(its)} items, {ts} trial-seconds")
            continue
        if a.tiny:
            its = its[:1] + its[-1:]
        t0 = time.time()
        n_exp = {"core": 12, "core_rep": 12, "core_bal": 10, "screen": 2 * len(X.screen_types())}
        total_ts = sum(n_exp[b] * 30 for _, b in its)
        done_ts, run_ts, run_s = 0, 0, 0.0
        for k, (v, bat) in enumerate(its):
            t1 = time.time()
            out = X.run_variant(v, bat, a.device, n_trials=2 if a.tiny else 30,
                                max_rows=a.max_rows or None, t_run=50.0 if a.tiny else 1000.0)
            dt = time.time() - t1
            done_ts += n_exp[bat] * 30
            if dt > 5:  # actually simulated (not skipped)
                run_ts += n_exp[bat] * 30
                run_s += dt
            rate = run_s / run_ts if run_ts else float("nan")  # wall s per trial-second
            eta_h = rate * (total_ts - done_ts) / 3600
            print(f"[{ph}] {k + 1}/{len(its)} items | {rate:.3f} s per trial-second | "
                  f"phase ETA {eta_h:.1f} h | elapsed {(time.time() - t0) / 3600:.2f} h", flush=True)


if __name__ == "__main__":
    main()
