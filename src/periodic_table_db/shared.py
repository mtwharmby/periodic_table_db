from dataclasses import dataclass, asdict, field
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

# Lists of names of tables (note order is important!):
# - in the standard database
TABLE_NAMES = [
    "Element", "AtomicWeight", "AtomicWeightType", "Ion"
]
# - in the extended database
TABLE_NAMES_EXTENDED = [
    "Period", "Group", "Block", "Label", "ElementLabel"
]


@dataclass
class Ion:
    symbol: str = field(init=False)
    element_symbol: str
    charge: int
    valence_state: bool
    atomic_number: int | None = None

    def __post_init__(self):
        if self.charge > 0:
            self.symbol = f"{self.element_symbol}{abs(self.charge)}+"
        elif self.charge < 0:
            self.symbol = f"{self.element_symbol}{abs(self.charge)}-"
        elif self.valence_state:
            self.symbol = f"{self.element_symbol}val"
        else:
            self.symbol = f"{self.element_symbol}"

    dict = asdict


ion_symbol_re = re.compile(
    r"(^[A-Z][a-z]?)(?:(?:(\d+)?([+]+|-+))|(?:\((I+)\))?)$"
    r"|^(?:([A-Z][a-z]?(?=val?$))(val?)?)$"
)


def parse_ion_symbol(symbol: str, atomic_nr: int = None):
    symbol_parts = ion_symbol_re.match(symbol)
    if symbol_parts is None:
        raise RuntimeError(f"Cannot parse ion symbol {symbol}")

    if symbol_parts.group(1):
        # First line of the regex has been found...
        elem_symbol = symbol_parts.group(1)
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
            if "-" in symbol_parts.group(3):
                charge = -charge
        elif symbol_parts.group(4) is not None:
            # e.g. Fe(III) - no possibility to handle -ve charge here
            charge = len(symbol_parts.group(4))
        else:
            charge = 0
        val = False

    else:
        # Second line of regex has been found
        # Ion is in valence state
        elem_symbol = symbol_parts.group(5)
        charge = 0
        val = True

    return {
        "element_symbol": elem_symbol,
        "charge": charge,
        "atomic_number": atomic_nr,
        "valence_state": val
    }
