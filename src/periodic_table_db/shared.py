from dataclasses import dataclass, asdict
import re

ATOMIC_NR = "atomic_number"
ELEM_SYMBOL = "symbol"

AT_WEIGHT = "weight"
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

TABLE_NAMES = [
    "Element", "AtomicWeight", "AtomicWeightType", "Ion"
]

TABLE_NAMES_EXTENDED = [
    "Period", "Group", "Block", "Label", "ElementLabel"
]


@dataclass
class Ion:
    symbol: str
    charge: int
    atomic_number: int | None = None

    dict = asdict

    @property
    def element_symbol(self):
        symbol_parts = ion_symbol_re.match(self.symbol)
        return symbol_parts.group(1)


ion_symbol_re = re.compile(
    r"(^[A-Z][a-z]?)(?:(?:(\d+)?([+-])(\3)*)?|(?:\((I+)\))?)$"
)


def parse_ion_symbol(symbol: str, atomic_nr: int = None):
    symbol_parts = ion_symbol_re.match(symbol)
    if symbol_parts is None:
        raise RuntimeError(f"Cannot parse ion symbol {symbol}")

    elem_symbol = symbol_parts.group(1)
    charge = 0
    if symbol_parts.group(2) is not None:
        charge = int(symbol_parts.group(2))
        if symbol_parts.group(3) == "+":
            pass
        elif symbol_parts.group(3) == "-":
            charge = -charge
        else:
            raise RuntimeError(f"Cannot parse ion symbol {symbol}")
    elif symbol_parts.group(3) is not None:
        charge = len(symbol_parts.group(3))
        if "-" in symbol_parts:
            charge = -charge

    return {
        "element_symbol": elem_symbol,
        "charge": charge,
        "atomic_number": atomic_nr
    }


def ion_factory(element_symbol, charge, atomic_number=None):
    if charge > 0:
        symbol = f"{element_symbol}{abs(charge)}+"
    elif charge < 0:
        symbol = f"{element_symbol}{abs(charge)}-"
    else:
        symbol = f"{element_symbol}"

    return Ion(
        symbol=symbol,
        charge=charge,
        atomic_number=atomic_number
    )
