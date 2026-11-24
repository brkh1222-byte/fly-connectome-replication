# Brian2 semantics of the Shiu model (measured, 2026-11-24)

Measured with brian2 2.9.0 on Shiu's own `default_params` (scratch probes; see the commit
that added this note). These define what `src/lif_torch.py` must reproduce.

1. **Schedule per 0.1 ms step:** `groups` (state update) -> `thresholds` -> `synapses`
   (spike delivery and PoissonInput) -> `resets`.
2. **Integration:** exact solution of the linear ODE (`method='linear'`):
   `g' = g e^{-dt/tau}`, `v' = v_0 + (v - v_0) e^{-dt/tau_m} + g * tau/(tau_m - tau) * (e^{-dt/tau_m} - e^{-dt/tau})`,
   applied only where `not_refractory = timestep(t - lastspike) >= timestep(rfc)`.
3. **Refractoriness freezes v and g** (both are flagged `(unless refractory)`).
4. **Synaptic input that arrives while the target is refractory is discarded.** Probe: neuron 0
   spikes at t = 0 with rfc = 10 ms and receives a 5 mV synaptic event at t = 1.8 ms. g stays 0
   for the whole refractory period and afterwards. A control with rfc = 0.5 ms shows the event
   arriving at the 1.8 ms step (g = 5 mV at the next recorded step). Setting g by hand during
   refractoriness persists, so g is not reset each step: the synaptic `g += w` is skipped for
   refractory targets. (cerebro-mosca, Zenodo 10.5281/zenodo.23005090, reports the same.)
5. **Delay:** a spike at step s reaches its targets in the synapses slot of step s + 18.
6. **The reset string `v = v_rst; w = 0; g = 0 * mV`** runs without error. The `w = 0` term has
   no effect on the neuron state.
7. **Poisson-driven neurons** get `rfc = 0` and Bernoulli(rate x dt) kicks of
   w_syn x f_poi = 68.75 mV on v. On the spike step, the reset overwrites any kick.
8. `SpikeMonitor.count` is restored by `Network.restore()`, so the store/restore loop in
   `src/shiu_brian2.py` gives independent trials.
