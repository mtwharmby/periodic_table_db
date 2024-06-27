from ...shared import BLOCK

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

MAIN_GROUP = "Main Group"
TRANS_ELEM = "Transition Element"
RE_ELEM = "Rare Earth Element"
LANTHANOID = "Lanthanoid"
ACTINOID = "Actinoid"
ALKALI_METAL = "Alkali Metal"
ALKALINE_METAL = "Alkaline Earth Metal"
COIN_METAL = "Coinage Metal"
PNICTOGEN = "Pnictogen"
CHALCOGEN = "Chalcogens"
HALOGEN = "Halogen"
NOBLE_GAS = "Noble Gases"

labels = [
    {
        "name": MAIN_GROUP,
        "description": "Groups 1, 2 and 13-18 (excluding hydrogen)."
    }, {
        "name": TRANS_ELEM,
        "description": "d-block elements with whose atoms or cations have "
                       "partially filled d-subshells."
    }, {
        "name": RE_ELEM,
        "description": "Scandium, yttrium and the lanthanoids."
    }, {
        "name": LANTHANOID,
        "description": "f-block elements with partially filled 4f orbital. "
                       "Chemically similar to lanthanum. The term lanthanoid "
                       "is preferred to 'lanthanide'."
    }, {
        "name": ACTINOID,
        "description": "f-block elements with partially filled 5f orbital. "
                       "Chemically similar to actinium. The term actinoid "
                       "is preferred to 'actinide'."
    }, {
        "name": ALKALI_METAL,
        "description": "Group 1 element."
    }, {
        "name": ALKALINE_METAL,
        "description": "Group 2 element."
    }, {
        "name": COIN_METAL,
        "description": "Group 11 element."
    }, {
        "name": PNICTOGEN,
        "description": "Group 15 element."
    }, {
        "name": CHALCOGEN,
        "description": "Group 16 element."
    }, {
        "name": HALOGEN,
        "description": "Group 17 element."
    }, {
        "name": NOBLE_GAS,
        "description": "Group 18 element."
    }
]

"""
Labels:
- Main Group -> group 13-18 not H
- Transition Element -> group 3-11
- Rare Earth Element -> lanthanoids + Sc + Y
- Lanthanoid -> elements 57-71 incl.
- Actinoid -> elements 89-103 incl.
"""
label_rules = {
    MAIN_GROUP: lambda at: (at.atomic_nr != 1
                            and at.group in list(range(13, 19))),
    TRANS_ELEM: lambda at: at.group in list(range(3, 12)),
    RE_ELEM: lambda at: (at.atomic_nr in [21, 39]
                         or at.atomic_nr in list(range(57, 72))),
    LANTHANOID: lambda at: at.atomic_nr in list(range(57, 72)),
    ACTINOID: lambda at: at.atomic_nr in list(range(89, 104)),
    ALKALI_METAL: lambda at: at.group == 1,
    ALKALINE_METAL: lambda at: at.group == 2,
    COIN_METAL: lambda at: at.group == 11,
    PNICTOGEN: lambda at: at.group == 15,
    CHALCOGEN: lambda at: at.group == 16,
    HALOGEN: lambda at: at.group == 17,
    NOBLE_GAS: lambda at: at.group == 18,
}
