from .shared import (
    WEIGHT_TYPE_NONE, WEIGHT_TYPE_INTERVAL, WEIGHT_TYPE_REPORTED
)

atomic_weight_types = [
    {
        "name": WEIGHT_TYPE_NONE,
        "method": "none",
        "reason": "No stable isotope(s) with characteristic isotopic "
                  "composition exist. A standard atomic weight cannot be "
                  "determined."
    },
    {
        "name": WEIGHT_TYPE_INTERVAL,
        "method": "calculated",
        "reason": "CIAAW expresses atomic weight as an interval intended to "
                  "encompass all \"normal\" materials. Atomic weight has been "
                  "calculated as the midpoint of the interval; uncertainty is "
                  "calculated as half the difference between the maximum and "
                  "minimum of the interval."
    },
    {
        "name": WEIGHT_TYPE_REPORTED,
        "method": "tabulated",
        "reason": "CIAAW provides a single value for the atomic weight with "
                  "an uncertainty. The quoted atomic weight is representative "
                  "of the population of a sample of atoms of the element. A "
                  "minimum and maximum weight have been calculated from the "
                  "uncertainty."
    }
]
