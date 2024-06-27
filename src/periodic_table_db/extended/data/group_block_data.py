from ...shared import BLOCK

# TODO Add citations!

groups = [
    {
        "number": 1,
        "label_eu": "IA",
        "label_us": "IA",
        "name": "Alkali Metals"
    }, {
        "number": 2,
        "label_eu": "IIA",
        "label_us": "IIA",
        "name": "Alkaline Earth Metals"
    }, {
        "number": 3,
        "label_eu": "IIIA",
        "label_us": "IIIB",
        "name": None
    }, {
        "number": 4,
        "label_eu": "IVA",
        "label_us": "IVB",
        "name": None
    }, {
        "number": 5,
        "label_eu": "VA",
        "label_us": "VB",
        "name": None
    }, {
        "number": 6,
        "label_eu": "VIA",
        "label_us": "VIB",
        "name": None
    }, {
        "number": 7,
        "label_eu": "VIIA",
        "label_us": "VIIB",
        "name": None
    }, {
        "number": 8,
        "label_eu": "VIIIA",
        "label_us": "VIIIB",
        "name": None
    }, {
        "number": 9,
        "label_eu": "VIIIA",
        "label_us": "VIIIB",
        "name": None
    }, {
        "number": 10,
        "label_eu": "VIIIA",
        "label_us": "VIIIB",
        "name": None
    }, {
        "number": 11,
        "label_eu": "IB",
        "label_us": "IB",
        "name": "Coinage Metals"
    }, {
        "number": 12,
        "label_eu": "IIB",
        "label_us": "IIB",
        "name": None
    }, {
        "number": 13,
        "label_eu": "IIIB",
        "label_us": "IIIA",
        "name": None
    }, {
        "number": 14,
        "label_eu": "IVB",
        "label_us": "IVA",
        "name": None
    }, {
        "number": 15,
        "label_eu": "VB",
        "label_us": "VA",
        "name": "Pnictogens"
    }, {
        "number": 16,
        "label_eu": "VIB",
        "label_us": "VIA",
        "name": "Chalcogens"
    }, {
        "number": 17,
        "label_eu": "VIIB",
        "label_us": "VIIA",
        "name": "Halogens"
    }, {
        "number": 18,
        "label_eu": "VIIIB",
        "label_us": "VIIIA",
        "name": "Noble Gases"
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

labels = [
    {
        "name": MAIN_GROUP,
        "description": "Groups 1, 2 and 13-18 (excluding hydrogen)."
    },
    {
        "name": TRANS_ELEM,
        "description": "d-block elements with whose atoms or cations have "
                       "partially filled d-subshells."
    },
    {
        "name": RE_ELEM,
        "description": "Scandium, yttrium and the lanthanoids."
    },
    {
        "name": LANTHANOID,
        "description": "f-block elements with partially filled 4f orbital. "
                       "Chemically similar to lanthanum. The term lanthanoid "
                       "is preferred to 'lanthanide`"
    },
    {
        "name": ACTINOID,
        "description": "f-block elements with partially filled 5f orbital. "
                       "Chemically similar to actinium. The term actinoid "
                       "is preferred to 'actinide`"
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
}
