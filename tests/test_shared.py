import pytest

from periodic_table_db.shared import parse_ion_symbol, Ion


class TestParseIonSymbol:

    @pytest.mark.parametrize(
            "symbol_nr, exp", [
                (("Li+", None), {
                    "element_symbol": "Li",
                    "charge": 1,
                    "atomic_number": None
                }),
                (("Be++", 4), {
                    "element_symbol": "Be",
                    "charge": 2,
                    "atomic_number": 4
                }),
                (("O--", 8), {
                    "element_symbol": "O",
                    "charge": -2,
                    "atomic_number": 8
                }),
                (("S2-", None), {
                    "element_symbol": "S",
                    "charge": -2,
                    "atomic_number": None
                }),
                (("Fe(III)", None), {
                    "element_symbol": "Fe",
                    "charge": 3,
                    "atomic_number": None
                }),
                (("C", 6), {
                    "element_symbol": "C",
                    "charge": 0,
                    "atomic_number": 6
                })
            ]
    )
    def test_parse(self, symbol_nr: tuple[str, int | None],
                   exp: dict[str, str | int | None]):
        out = parse_ion_symbol(*symbol_nr)
        assert out == exp

    @pytest.mark.parametrize(
            "symbol", ["Li+-", "O2--", "Fe(III)3+"]
    )
    def test_parse_fail(self, symbol):
        with pytest.raises(RuntimeError):
            parse_ion_symbol(symbol)


class TestIon:

    @pytest.mark.parametrize(
            "in_dict, exp", [
                ({
                    "element_symbol": "O",
                    "charge": -2,
                    "atomic_number": 8
                }, "O2-"),
                ({
                    "element_symbol": "Fe",
                    "charge": 3,
                    "atomic_number": None
                }, "Fe3+"),
                ({
                    "element_symbol": "C",
                    "charge": 0,
                    "atomic_number": 6
                }, "C")
            ]
    )
    def test_symbol(self, in_dict: dict[str, str | int | None],
                    exp: Ion):
        ion = Ion(**in_dict)
        assert ion.symbol == exp
