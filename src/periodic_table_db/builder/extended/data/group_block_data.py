from dataclasses import dataclass
from collections.abc import Callable

from .electronic_structure import Atom
from ....shared import BLOCK

# TODO Add citations!

groups = [
    {
        "number": 1,
        "label_eu": "IA",
        "label_us": "IA",
    }, {
        "number": 2,
        "label_eu": "IIA",
        "label_us": "IIA",
    }, {
        "number": 3,
        "label_eu": "IIIA",
        "label_us": "IIIB",
    }, {
        "number": 4,
        "label_eu": "IVA",
        "label_us": "IVB",
    }, {
        "number": 5,
        "label_eu": "VA",
        "label_us": "VB",
    }, {
        "number": 6,
        "label_eu": "VIA",
        "label_us": "VIB",
    }, {
        "number": 7,
        "label_eu": "VIIA",
        "label_us": "VIIB",
    }, {
        "number": 8,
        "label_eu": "VIIIA",
        "label_us": "VIIIB",
    }, {
        "number": 9,
        "label_eu": "VIIIA",
        "label_us": "VIIIB",
    }, {
        "number": 10,
        "label_eu": "VIIIA",
        "label_us": "VIIIB",
    }, {
        "number": 11,
        "label_eu": "IB",
        "label_us": "IB",
    }, {
        "number": 12,
        "label_eu": "IIB",
        "label_us": "IIB",
    }, {
        "number": 13,
        "label_eu": "IIIB",
        "label_us": "IIIA",
    }, {
        "number": 14,
        "label_eu": "IVB",
        "label_us": "IVA",
    }, {
        "number": 15,
        "label_eu": "VB",
        "label_us": "VA",
    }, {
        "number": 16,
        "label_eu": "VIB",
        "label_us": "VIA",
    }, {
        "number": 17,
        "label_eu": "VIIB",
        "label_us": "VIIA",
    }, {
        "number": 18,
        "label_eu": "VIIIB",
        "label_us": "VIIIA",
    },
 ]

blocks = [
    {BLOCK: "s"},
    {BLOCK: "p"},
    {BLOCK: "d"},
    {BLOCK: "f"},
]

# MAIN_GROUP = "Main Group"
# TRANS_ELEM = "Transition Element"
# RE_ELEM = "Rare Earth Element"
# LANTHANOID = "Lanthanoid"
# ACTINOID = "Actinoid"
# ALKALI_METAL = "Alkali Metal"
# ALKALINE_METAL = "Alkaline Earth Metal"
# COIN_METAL = "Coinage Metal"
PNICTOGEN = "Pnictogen"
CHALCOGEN = "Chalcogens"
HALOGEN = "Halogen"
NOBLE_GAS = "Noble Gases"


@dataclass
class LabelDefinition:
    name: str
    description: str
    rule: Callable[[Atom], bool]


"""
Labels:
- Main Group -> group 13-18 not H
- Transition Element -> group 3-11
- Rare Earth Element -> lanthanoids + Sc + Y
- Lanthanoid -> elements 57-71 incl.
- Actinoid -> elements 89-103 incl.
- Alkali Metal -> Group 1
- Alkaline Earth Metal -> Group 2
- Coinage Metal -> Group 11
- Pnictogen -> Group 15
- Chalcogen -> Group 16
- Halogen -> Group 17
- Noble Gas -> Group 18
"""
label_definitions = [
    LabelDefinition(
        name="Main Group",
        description="Groups 1, 2 and 13-18 (excluding hydrogen).",
        rule=lambda at: at.atomic_nr != 1 and at.group in list(range(13, 19))
    ),
    LabelDefinition(
        name="Transition Element",
        description="d-block elements with whose atoms or cations have "
                    "partially filled d-subshells.",
        rule=lambda at: at.group in list(range(3, 12))
    ),
    LabelDefinition(
        name="Rare Earth Element",
        description="Scandium, yttrium and the lanthanoids.",
        rule=lambda at: (at.atomic_nr in [21, 39]
                         or at.atomic_nr in list(range(57, 72)))
    ),
    LabelDefinition(
        name="Lanthanoid",
        description="f-block elements with partially filled 4f orbital. "
                    "Chemically similar to lanthanum. The term lanthanoid "
                    "is preferred to 'lanthanide'.",
        rule=lambda at: at.atomic_nr in list(range(57, 72))
    ),
    LabelDefinition(
        name="Actinoid",
        description="f-block elements with partially filled 5f orbital. "
                    "Chemically similar to actinium. The term actinoid "
                    "is preferred to 'actinide'.",
        rule=lambda at: at.atomic_nr in list(range(89, 104))
    ),
    LabelDefinition(
        name="Alkali Metal",
        description="Group 1 element.",
        rule=lambda at: at.group == 1
    ),
    LabelDefinition(
        name="Alkaline Earth Metal",
        description="Group 2 element.",
        rule=lambda at: at.group == 2
    ),
    LabelDefinition(
        name="Coinage Metal",
        description="Group 11 element.",
        rule=lambda at: at.group == 11
    ),
    LabelDefinition(
        name="Pnictogen",
        description="Group 15 element.",
        rule=lambda at: at.group == 15
    ),
    LabelDefinition(
        name="Chalcogen",
        description="Group 16 element.",
        rule=lambda at: at.group == 16
    ),
    LabelDefinition(
        name="Halogen",
        description="Group 17 element.",
        rule=lambda at: at.group == 17
    ),
    LabelDefinition(
        name="Noble Gases",
        description="Group 18 element.",
        rule=lambda at: at.group == 18
    ),
]

# label_values contains the values needed to populate the Labels table
label_values = [
    {"name": lab.name, "description": lab.description}
    for lab in label_definitions
]
# label_rules contain the rules used to apply labels to an atom
label_rules = {
    lab.name: lab.rule
    for lab in label_definitions
}
