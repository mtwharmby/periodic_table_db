from dataclasses import dataclass, asdict

from ..shared import (  # noqa: F401
    ATOMIC_NR, ELEM_SYMBOL, AT_WEIGHT, WEIGHT_TYPE_NONE, WEIGHT_TYPE_INTERVAL,
    WEIGHT_TYPE_REPORTED, ION_ID, ION_SYMBOL, ION_CHARGE, E_SHELL_STRUCT,
    E_SUB_SHELL_STRUCT, PERIOD, GROUP, BLOCK, BLOCK_ID, LABEL, LABEL_ID
)


@dataclass
class AtomicWeight:
    weight: float
    weight_esd: float
    weight_min: float
    weight_max: float
    weight_type: str

    dict = asdict


@dataclass
class Element:
    atomic_number: int
    symbol: str
    name: str
    weight: AtomicWeight

    dict = asdict
