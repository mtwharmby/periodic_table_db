from .. import Element
from .data import Atom


def get_electronic_structure(elements: list[Element]):
    return [
        Atom(el.atomic_number)
        for el in elements
    ]
