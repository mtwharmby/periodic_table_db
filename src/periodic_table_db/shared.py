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

ION_SYMBOL = "symbol"
ION_CHARGE = "charge"


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


@dataclass
class Ion:
    element_symbol: str
    charge: int
    atomic_number: int = None
    symbol: str = None

    def dict(self):
        if not self.symbol:
            if self.charge > 0:
                self.symbol = f"{self.element_symbol}{self.charge}+"
            elif self.charge < 0:
                self.symbol = f"{self.element_symbol}{self.charge}-"
            else:
                self.symbol = f"{self.element_symbol}"

        d = asdict(self)
        del d["element_symbol"]
        return d
