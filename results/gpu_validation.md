# PyTorch LIF (float32) vs Brian2 (float64) validation (T2.2)

FlyWire v783, Shiu parameters, 30 trials x 1 s per run. Brian2 2.9.0 (Cython) seeds 11/12; PyTorch seeds 21/22.
Criteria (pre-specified, src/validate.py): r(torch, brian2) >= r(brian2, brian2) - 0.01 for both replicate pairs; readout 95% CIs overlap; total spikes per trial Mann-Whitney p > 0.01.

| device   | experiment                 | readout   |   r_brian2_brian2 |   r_torch_brian2 |   r_torch_brian2_rep |   r_torch_torch |   n_active | readout_brian2    | readout_torch     |   total_spikes_brian2 |   total_spikes_torch |   p_total_spikes |   torch_seconds_30trials | PASS   |
|:---------|:---------------------------|:----------|------------------:|-----------------:|---------------------:|----------------:|-----------:|:------------------|:------------------|----------------------:|---------------------:|-----------------:|-------------------------:|:-------|
| mps      | sugarR_100Hz               | MN9_L     |           0.99967 |          0.99943 |              0.9996  |         0.99961 |        399 | 61.4 [59.7, 63.0] | 62.7 [60.8, 64.6] |               8886.7  |              9086.97 |          0.04841 |                 189.904  | True   |
| mps      | sugarR_100Hz_bitterR_100Hz | MN9_L     |           0.99965 |          0.9997  |              0.99949 |         0.99954 |        386 | 3.5 [2.5, 4.4]    | 2.9 [2.2, 3.6]    |               8721.07 |              8703.63 |          0.92344 |                  94.3609 | True   |
| mps      | JO_CE_100Hz                | aBN1      |           0.9995  |          0.99945 |              0.99969 |         0.99954 |        320 | 25.9 [25.2, 26.7] | 26.2 [25.3, 27.0] |               9383.3  |              9395.23 |          0.75618 |                 345.229  | True   |
| cpu      | sugarR_100Hz               | MN9_L     |           0.99967 |          0.9997  |              0.99957 |         0.99975 |        403 | 61.4 [59.7, 63.0] | 62.7 [61.1, 64.2] |               8886.7  |              9020.1  |          0.19072 |                 481.953  | True   |

**MPS (Apple M4 GPU, float32): PASS on 3/3 experiments.**
**CPU (float32): PASS on 1/3 experiments run.** The other two CPU runs were stopped: during 19:30-22:30 the machine was oversubscribed by other jobs (load average about 31 on 10 cores), and one CPU run took 10,823 s instead of 482 s. MPS and CPU run the same code path, and with the same seed and the CPU RNG they gave identical spike counts in an earlier test.

The torch_seconds column is wall time on a heavily shared machine and is not a benchmark. CUDA (cloud) is validated with the same script as the first step of scripts/run_sweeps.sh.
