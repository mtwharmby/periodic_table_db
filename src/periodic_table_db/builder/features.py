from dataclasses import dataclass
import logging
import math
import re

import requests
from bs4 import BeautifulSoup

from .shared import (
    WEIGHT_TYPE_NONE, WEIGHT_TYPE_INTERVAL, WEIGHT_TYPE_REPORTED,
    Element, AtomicWeight
)


PERIODIC_TABLE_URL = "https://ciaaw.org/atomic-weights.htm"

logger = logging.getLogger(__name__)


@dataclass
class RawElement:
    atomic_nr: int
    symbol: str
    name: str
    atomic_weight_tabulated: list[str]


def get_elements_from_html(resp: requests.Response) -> list[RawElement]:
    """
    Returns list of elements with string properties from supplied html reponse.
    """
    soup = BeautifulSoup(resp.text, "html.parser")

    logger.info("Processing element rows.")
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


def parse_elements_text(raw_elements: list[RawElement]) -> list[Element]:
    """
    Returns a list of elements with properties with types as required for
    database entries.
    """

    def get_precision(number: str):
        """
        Returns the number of digits after the decimal place for a string
        representing a number.
        """
        return len(number.split(".")[1])

    # regex to differentiate one and no weight
    one_weight_regex = re.compile(r"(\d*\.\d*)\((\d\d?)\)")

    # Define a constant for the case where no weight is given
    NO_WEIGHT = AtomicWeight(
                    weight=None, weight_esd=None, weight_min=None,
                    weight_max=None, weight_type=WEIGHT_TYPE_NONE
                )

    logger.info("Processing scraped text to element properties.")
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
            logger.debug(f"Element '{raw.symbol}' atomic weight quoted as "
                         f"'{WEIGHT_TYPE_INTERVAL}' type. Weight calculated.")

        elif len(raw.atomic_weight_tabulated) == 1:
            # Atomic weight quoted either as a best value or none
            # Use regex to decide:
            mtch = one_weight_regex.search(raw.atomic_weight_tabulated[0])

            # N.B. next line: em-dash, not a hyphen!
            if not mtch and raw.atomic_weight_tabulated[0] == "—":
                at_weight = NO_WEIGHT
                logger.debug(f"Element '{raw.symbol}' atomic weight is "
                             f"'{WEIGHT_TYPE_NONE}' type. Assigned to 'None' "
                             "weight.")

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
                logger.debug(f"Element '{raw.symbol}' atomic weight is "
                             f"'{WEIGHT_TYPE_REPORTED}' type. Weight min and "
                             "max calculated.")

        elements.append(Element(
            atomic_number=raw.atomic_nr,
            symbol=raw.symbol,
            name=raw.name,
            weight=at_weight
        ))

    return elements


def get_elements(url: str = PERIODIC_TABLE_URL):
    """
    Entry point for parsing PERIODIC_TABLE_URL website and table therein.
    Returns parsed list of elements.
    """
    logger.info(f"Getting URL: {url}")
    html = requests.get(url)
    raw_elements = get_elements_from_html(html)
    return parse_elements_text(raw_elements)
