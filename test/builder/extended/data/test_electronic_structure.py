import pytest

from periodic_table_db.builder.extended.data.electronic_structure import (
    SubShell, Atom
)


class TestSubShell:

    def test_init(self):
        sub_shell = SubShell(3, 2)

        assert len(sub_shell.orbitals) == 5
        assert sub_shell.electrons == 0
        assert sub_shell.name == "3d"
        assert not sub_shell.is_full

    def test_populate(self):
        sub_shell = SubShell(3, 2)

        assert sub_shell.orbitals == [0] * 5

        population = {"electrons": 5, "sequence": []}

        rest = sub_shell.populate(population)
        assert sub_shell.orbitals == [1] * 5
        assert rest == {"electrons": 0, "sequence": [(3, 2)]}
        assert not sub_shell.is_full

    def test_populate_fill(self):
        sub_shell = SubShell(3, 2)

        assert sub_shell.orbitals == [0] * 5

        population = {"electrons": 12, "sequence": []}

        rest = sub_shell.populate(population)
        assert sub_shell.orbitals == [2] * 5
        assert rest == {"electrons": 2, "sequence": [(3, 2)]}
        assert sub_shell.is_full

    def test_add_electrons_noargs(self):
        sub_shell = SubShell(3, 2)
        assert sub_shell.electrons == 0

        rest = sub_shell.add_electrons()
        assert rest == 0
        assert sub_shell.electrons == 1

    def test_add_electrons(self):
        sub_shell = SubShell(3, 2)
        assert sub_shell.electrons == 0

        rest = sub_shell.add_electrons(6)
        assert rest == 0
        assert sub_shell.electrons == 6
        assert sub_shell.orbitals == [2, 1, 1, 1, 1]

        rest = sub_shell.add_electrons(6)
        assert rest == 2
        assert sub_shell.electrons == 10
        assert sub_shell.orbitals == [2, 2, 2, 2, 2]

    def test_remove_electrons_noargs(self):
        sub_shell = SubShell(3, 2)
        rest = sub_shell.add_electrons(9)

        sub_shell.remove_electrons()
        assert rest == 0
        assert sub_shell.electrons == 8
        assert sub_shell.orbitals == [2, 2, 2, 1, 1]

    def test_remove_electrons(self):
        sub_shell = SubShell(3, 2)
        sub_shell.add_electrons(9)

        rest = sub_shell.remove_electrons(2)
        assert rest == 0
        assert sub_shell.electrons == 7
        assert sub_shell.orbitals == [2, 2, 1, 1, 1]

        rest = sub_shell.remove_electrons(9)
        assert rest == -2
        assert sub_shell.electrons == 0

    def test_str(self):
        sub_shell = SubShell(3, 2)
        sub_shell.add_electrons(6)
        assert str(sub_shell) == "3d^{6}"

    def test_from_sub_shell_struct(self):
        sub_shell = SubShell.from_sub_shell_structure("5f^{9}")
        assert sub_shell._pqn == 5
        assert sub_shell._aqn == 3
        assert sub_shell.electrons == 9


class TestAtom:

    @pytest.mark.parametrize(
            "at_nr, period, group",
            [(2, 1, 18),    # He
             (6, 2, 14),    # C
             (26, 4, 8),    # Fe
             (62, 6, -1),   # Sm
             (74, 6, 6),    # W
             (87, 7, 1),    # Fr
             (111, 7, 11),  # Rg
             ])
    def test_group_period_calculation(self, at_nr, period, group):
        at = Atom(at_nr)
        assert at.period == period
        assert at.group == group

    @pytest.mark.parametrize(
            "at_nr, shell_struct",
            [(2, "2"),  # He
             (26, "2.8.14.2"),  # Fe
             (51, "2.8.18.18.5"),  # Sb
             (79, "2.8.18.32.18.1"),  # Au
             ]
    )
    def test_shell_structure(self, at_nr, shell_struct):
        at = Atom(at_nr)
        assert at.shell_structure == shell_struct

    @pytest.mark.parametrize(
        "at_nr, sub_shell_struct",
        [(2, "1s^{2}"),
         # Note: this is the wrong ground state or Cu, but is correct following
         # the rules.
         (29, "1s^{2}.2s^{2}.2p^{6}.3s^{2}.3p^{6}.3d^{9}.4s^{2}")
         ]
    )
    def test_sub_shell_structure(self, at_nr, sub_shell_struct):
        at = Atom(at_nr)
        assert at.sub_shell_structure == sub_shell_struct

    @pytest.mark.parametrize(
        "at_nr, correction, electrons, sub_shell_struct",
        [(29, "3d^{10}.4s^{1}", 29, "1s^{2}.2s^{2}.2p^{6}.3s^{2}.3p^{6}."
                                    "3d^{10}.4s^{1}")
         ]
    )
    def test_correct_orbital_filling(
        self, at_nr, correction, electrons, sub_shell_struct
    ):
        at = Atom(at_nr)
        assert at.electrons == electrons
        at.correct_orbital_filling(correction)
        assert at.electrons == electrons
        assert at.sub_shell_structure == sub_shell_struct
