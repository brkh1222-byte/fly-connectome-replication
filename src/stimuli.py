"""Type-based stimulus sets and readouts, defined identically in every dataset.

Stimuli use FlyWire (Schlegel et al. 2024) type names, which the male CNS ('flywireType')
and BANC (matches to FlyWire) carry too:
  sugar  LB3b + LB3c   (FlyWire sub-classes 'sugar' and 'sugar/low_salt')
  bitter LB1a-d
  water  LB3a
  JO_CE  Johnston's-organ types JO-C* and JO-E*
  JO_F   JO-F*
Side is the neuron's own side label in each dataset ("L"/"R"). Shiu's "right" sets are on
FlyWire side 'left'.
Readouts: MN9 = FlyWire type CB0701 (male CNS type MN9); aBN1 = SAD093.
The Shiu-exact neuron lists (src/experiments_def.py) are used for the FlyWire reproduction.
"""
import re

import numpy as np

STIM = {
    "sugar": lambda t: t in ("LB3b", "LB3c"),
    "bitter": lambda t: t in ("LB1a", "LB1b", "LB1c", "LB1d"),
    "water": lambda t: t == "LB3a",
    "JO_CE": lambda t: bool(re.match(r"^JO-[CE]", t)),
    "JO_F": lambda t: bool(re.match(r"^JO-F", t)),
}
READOUTS = {"MN9": "CB0701", "aBN1": "SAD093"}


def stim_idx(neurons, name, side):
    t = neurons.type.fillna("").astype(str)
    m = t.map(STIM[name]).values.astype(bool) & (neurons.side.values == side)
    return np.flatnonzero(m)


def readout_idx(neurons, name, side=None):
    m = neurons.type.values == READOUTS[name]
    if side is not None:
        m &= neurons.side.values == side
    return np.flatnonzero(m)


def stim_types(neurons, name):
    t = neurons.type.fillna("").astype(str)
    return sorted(set(t[t.map(STIM[name]).astype(bool)]))
