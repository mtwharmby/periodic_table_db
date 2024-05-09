from dataclasses import dataclass, asdict


ATOMIC_NR = "atomic_number"
ELEM_SYMBOL = "symbol"
ELEM_NAME = "name"
ELEM_WEIGHT_ID = "atomic_weight_id"

AT_WEIGHT = "weight"
AT_WEIGHT_ESD = "weight_esd"
AT_WEIGHT_MIN = "weight_min"
AT_WEIGHT_MAX = "weight_max"
AT_WEIGHT_TYPE_ID = "weight_type_id"

WEIGHT_TYPE_NONE = "None"
WEIGHT_TYPE_INTERVAL = "Interval"
WEIGHT_TYPE_REPORTED = "Reported"


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
