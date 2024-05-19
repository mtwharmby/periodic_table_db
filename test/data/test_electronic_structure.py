import pytest

from periodic_table_db.extended.data.electronic_structure import SubShell, Atom


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
