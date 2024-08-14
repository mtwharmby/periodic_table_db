from contextlib import nullcontext
import logging

from sqlalchemy import Engine, MetaData, Connection, insert, select

from ..dbconnector import DBConnector

from ..shared import (
    ATOMIC_NR, ELEM_SYMBOL, ION_ID, ION_SYMBOL, TABLE_NAMES,
    TABLE_NAMES_EXTENDED, Ion
)


logger = logging.getLogger(__name__)


class PeriodicTableDBAPI(DBConnector):

    def __init__(
            self, engine: Engine, md: MetaData, extended=False, **kwargs
    ):
        super().__init__(engine, md)

        tab_names = list(TABLE_NAMES)
        if extended:
            tab_names.extend(TABLE_NAMES_EXTENDED)

        self.tables = self.get_tables_from_existing(tab_names, **kwargs)

    def get_atomic_nr_for_symbol(
            self, symbol: str, conn: Connection = None
    ) -> int | None:
        """
        Get the atomic number of an element from its symbol.
        """
        atomic_nr_stmt = (
            select(self.tables["Element"].c[ATOMIC_NR])
            .where(self.tables["Element"].c[ELEM_SYMBOL] == symbol)
        )

        with (nullcontext(conn) if conn else self.connect()) as conn:
            atomic_nr_res = conn.execute(atomic_nr_stmt)
            return atomic_nr_res.scalar_one_or_none()

    def add_ions(self, ions: Ion | list[Ion], conn: Connection = None):
        if isinstance(ions, Ion):
            ions = [ions, ]

        with (nullcontext(conn) if conn else self.connect()) as conn:
            ion_values = []
            for elem_ion in ions:
                if elem_ion.atomic_number is None:
                    at_nr = self.get_atomic_nr_for_symbol(
                        elem_ion.symbol, conn
                    )
                    if at_nr is None:
                        raise RuntimeError(
                            f"Cannot find atomic number for {elem_ion}."
                        )
                    elem_ion.atomic_number = at_nr
                ion_values.append(elem_ion.dict())

            if len(ions) == 1:
                msg = f"Adding entry for '{ions[0].symbol}' to"
            else:
                msg = f"Adding {len(ion_values)} entries to"
            logger.info(f"{msg} {self.tables["Ion"].name} table.")
            conn.execute(insert(self.tables["Ion"]), ion_values)
            conn.commit()

    def get_ids_for_ion_symbols(
            self, ion_symbols: str | list[str], conn: Connection = None
    ) -> dict[str, int]:
        if isinstance(ion_symbols, str):
            ion_symbols = [ion_symbols, ]

        ion_symbol_ids_stmt = (
            select(
                self.tables["Ion"].c[ION_SYMBOL],
                self.tables["Ion"].c[ION_ID]
            ).where(self.tables["Ion"].c[ION_SYMBOL].in_(ion_symbols))
        )

        with (nullcontext(conn) if conn else self.connect()) as conn:
            ion_symbol_ids_res = conn.execute(ion_symbol_ids_stmt)
            return dict(ion_symbol_ids_res.t.all())
