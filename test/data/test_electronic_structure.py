from periodic_table_db.data.electronic_structure import SubShell


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
