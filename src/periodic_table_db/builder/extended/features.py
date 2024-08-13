from ..shared import Element
from .data import Atom, label_rules
from .data.electronic_structure import GROUND_STATES


def get_electronic_structure(elements: list[Element]):
    """
    Generate the electronic structures for the elements provided.
    """
    return [
        Atom(el.atomic_number)
        for el in elements
    ]


def correct_ground_states(atoms: list[Atom]):
    """
    Correct the ground state electronic configuration of all atoms having
    corresponding entry in the GROUND_STATES dictionary.
    """
    for atom in atoms:
        if atom.atomic_nr in GROUND_STATES:
            atom.correct_orbital_filling(GROUND_STATES[atom.atomic_nr])


def add_labels(atoms: list[Atom]):
    """
    Adds labels to atoms based on the rules in label_rules.
    Labels are derived from properties of the electronic configurations
    (e.g. group) or atomic number.
    """
    for atom in atoms:
        for label in label_rules:
            if label_rules[label](atom):
                atom.labels.append(label)
