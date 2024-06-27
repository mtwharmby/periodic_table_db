from dataclasses import dataclass, asdict
import re


ATOMIC_NR = "atomic_number"
ELEM_SYMBOL = "symbol"
ELEM_NAME = "name"
ELEM_WEIGHT_ID = "atomic_weight_id"
ELEM_BLOCK_ID = "block_id"

AT_WEIGHT = "weight"
AT_WEIGHT_ESD = "weight_esd"
AT_WEIGHT_MIN = "weight_min"
AT_WEIGHT_MAX = "weight_max"
AT_WEIGHT_TYPE_ID = "weight_type_id"

WEIGHT_TYPE_NONE = "None"
WEIGHT_TYPE_INTERVAL = "Interval"
WEIGHT_TYPE_REPORTED = "Reported"

ION_ID = "id"
ION_SYMBOL = "symbol"
ION_CHARGE = "charge"

E_SHELL_STRUCT = "shell_structure"
E_SUB_SHELL_STRUCT = "sub_shell_structure"

PERIOD = "period"
GROUP = "group"
BLOCK = "block"
BLOCK_ID = "id"
LABEL = "name"
LABEL_ID = "label_id"


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

    def dict(self) -> dict[str, int | str]:
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


ion_symbol_re = re.compile(r"(^[A-Z][a-z]?)(\d*)([+-]?)")


def make_ion_for_symbol(symbol: str, atomic_nr: int = None) -> Ion:
    symbol_parts = ion_symbol_re.search(symbol)
    assert symbol_parts is not None

    elem_symbol = symbol_parts.group(1)
    if symbol_parts.group(2):
        charge = int(symbol_parts.group(2))
        if symbol_parts.group(3) == "-":
            charge = -charge
    elif symbol_parts.group(3) == "+":
        charge = 1
    elif symbol_parts.group(3) == "-":
        charge = -1
    else:
        charge = 0

    return Ion(
        element_symbol=elem_symbol,
        charge=charge,
        symbol=symbol,
        atomic_number=atomic_nr
    )
