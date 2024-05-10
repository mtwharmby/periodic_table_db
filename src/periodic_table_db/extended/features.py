from .. import Element
from . import Atom


def generate_electronic_structure(elements: list[Element]):
    return [
        Atom(el.atomic_number)
        for el in elements
    ]
