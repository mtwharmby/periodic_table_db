from dataclasses import dataclass
import logging
import math
import re

import requests
from bs4 import BeautifulSoup

from . import (Element, AtomicWeight, WEIGHT_TYPE_NONE, WEIGHT_TYPE_INTERVAL,
               WEIGHT_TYPE_REPORTED)


PERIODIC_TABLE_URL = "https://ciaaw.org/atomic-weights.htm"

logger = logging.getLogger(__name__)


@dataclass
class RawElement:
    atomic_nr: int
    symbol: str
    name: str
    atomic_weight_tabulated: list[str]


def get_raw_elements(url: str) -> list[RawElement]:
    logger.info(f"Getting URL: {url}")
    html = requests.get(url)
    soup = BeautifulSoup(html.text, "html.parser")

    logger.info("Processing element rows...")
    raw_elements = []
    element_rows = soup.find("table").tbody.find_all("tr")
    for elem in element_rows:
        vals = elem.find_all("td")
        if len(vals) == 0:
            continue
        tabulated_weights = list(
            vals[3].text.replace("\xa0", "")  # Remove &nbsp;s
            .replace(" ", "")
            .strip("[").strip("]").split(",")
        )
        raw_elements.append(RawElement(
            atomic_nr=int(vals[0].text),
            symbol=vals[1].text,
            name=vals[2].text.capitalize(),
            atomic_weight_tabulated=tabulated_weights
        ))

    return raw_elements


def get_elements(raw_elements: list[RawElement]) -> list[Element]:

    def get_precision(value: str):
        # Find number of figures after dp
        return len(value.split(".")[1])

    # regex to differentiate one and no weight
    one_weight_regex = re.compile(r"(\d*\.\d*)\((\d\d?)\)")

    # Define a constant for the case where no weight is given
    NO_WEIGHT = AtomicWeight(
                    weight=None, weight_esd=None, weight_min=None,
                    weight_max=None, weight_type=WEIGHT_TYPE_NONE
                )

    elements = []
    for raw in raw_elements:

        if len(raw.atomic_weight_tabulated) == 2:
            # Atomic weight quoted as an interval - we find the midpoint
            weight_interval = list(map(float, raw.atomic_weight_tabulated))
            weight_min = min(weight_interval)
            weight_max = max(weight_interval)
            prec = get_precision(raw.atomic_weight_tabulated[0])
            esd = round((weight_max - weight_min) / 2, prec)

            at_weight = AtomicWeight(
                weight=round(weight_max - esd, prec),
                weight_esd=esd,
                weight_min=weight_min,
                weight_max=weight_max,
                weight_type=WEIGHT_TYPE_INTERVAL
            )

        elif len(raw.atomic_weight_tabulated) == 1:
            # Atomic weight quoted either as a best value or none
            # Use regex to decide:
            mtch = one_weight_regex.search(raw.atomic_weight_tabulated[0])

            # N.B. next line: em-dash, not a hyphen!
            if not mtch and raw.atomic_weight_tabulated[0] == "—":
                at_weight = NO_WEIGHT

            else:
                weight = float(mtch.group(1))
                prec = get_precision(mtch.group(1))
                esd = round(float(mtch.group(2)) * math.pow(10, -prec), prec)

                at_weight = AtomicWeight(
                    weight=weight,
                    weight_esd=esd,
                    weight_min=round(weight - esd, prec),
                    weight_max=round(weight + esd, prec),
                    weight_type=WEIGHT_TYPE_REPORTED
                )

        elements.append(Element(
            atomic_number=raw.atomic_nr,
            symbol=raw.symbol,
            name=raw.name,
            weight=at_weight
        ))

    return elements


def parse_table():
    raw_elements = get_raw_elements(PERIODIC_TABLE_URL)
    return get_elements(raw_elements)
