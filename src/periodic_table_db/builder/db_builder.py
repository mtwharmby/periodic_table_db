import logging
from contextlib import nullcontext

from sqlalchemy import (
    MetaData, insert, select, Connection, bindparam, null, or_, Engine,
)

from ..dbconnector import DBConnector
from ..dbapi import PeriodicTableDBAPI
from .shared import (
    Element, Ion, WEIGHT_TYPE_NONE, ATOMIC_NR, ELEM_SYMBOL, ION_ID
)
from .data import atomic_weight_types as at_weight_values
from .schema import (
    element_table, atomic_weight_table, atomic_weight_type_table, ions_table
)

logger = logging.getLogger(__name__)


class PeriodicTableDBBuilder(DBConnector):

    def __init__(
            self, engine: Engine, md: MetaData, extended: bool = False,
            **kwargs
    ) -> None:
        super().__init__(engine, md)

        self.element = element_table(
            self.metadata_obj, extended=extended, **kwargs
        )
        self.atomic_weight = atomic_weight_table(self.metadata_obj, **kwargs)
        self.atomic_weight_type = atomic_weight_type_table(
            self.metadata_obj, **kwargs
        )
        self.ion = ions_table(self.metadata_obj, extended=extended, **kwargs)
        self.ion_table_pk = f"{self.ion.name}.{ION_ID}"

    def create_db(self):
        """
        Initialises the elements database.

        Adds the three methods used to determine/report atomic weights.
        """
        logger.info("Initialising database.")
        self.metadata_obj.create_all(self.engine)

        self.dbapi = PeriodicTableDBAPI(self.engine, self.metadata_obj)

        self._add_atomic_weight_types()

    def _add_atomic_weight_types(self):
        """
        Create the constants in the atomic weight type table.
        """
        with self.connect() as conn:
            logger.info(
                f"Adding weight types to {self.atomic_weight_type.name} table."
            )
            conn.execute(
                insert(self.atomic_weight_type), at_weight_values
            )
            conn.commit()

    def add_elements(self, elements: list[Element], conn: Connection = None):
        """
        Adds elements and their atomic weights to database, based on a list of
        elements supplied to the function.
        """
        with (nullcontext(conn) if conn else self.connect()) as conn:
            element_values = []
            weight_values = []
            elements_as_ions = []

            for elem in elements:
                el = elem.dict()
                weight = el.pop("weight")
                el["weight"] = weight["weight"]
                el["weight_type"] = weight["weight_type"]
                element_values.append(el)
                if weight not in weight_values:
                    weight_values.append(weight)

                # For each element add an Ion:
                ion = Ion(elem.symbol, 0, elem.atomic_number)
                elements_as_ions.append(ion)

            # Insert the atomic weights
            # Use subquery to associate weight types with each weight
            weight_type_subq = (
                select(self.atomic_weight_type.c.id)
                .where(self.atomic_weight_type.c.name
                       == bindparam("weight_type"))
                .scalar_subquery()
            )
            weights_insert_stmt = (
                insert(self.atomic_weight)
                .values(weight_type_id=weight_type_subq)
            )
            logger.info(f"Adding {len(weight_values)} entries "
                        f"to {self.atomic_weight.name} table.")
            conn.execute(weights_insert_stmt, weight_values)
            conn.commit()

            # Insert the elements
            # Use subquery to associate the weights with each element
            weight_subq = (
                select(self.atomic_weight.c.id)
                .join(self.atomic_weight_type)
                .where(
                    self.atomic_weight_type.c.name == bindparam("weight_type"),
                    or_(
                        self.atomic_weight.c.weight == bindparam("weight"),
                        self.atomic_weight.c.weight == null(),
                    )
                ).scalar_subquery()
            )
            # or_ statement needed above, since bindparam returns "col = None"
            # rather than "col IS NULL". This is a variation on this:
            #     https://stackoverflow.com/q/21668606
            # There's probably a neater solution using a TypeDecorator, but
            # this works
            elements_insert_stmt = (
                insert(self.element).values(atomic_weight_id=weight_subq)
            )
            logger.info(f"Adding {len(element_values)} entries to "
                        f"{self.element.name} table.")
            conn.execute(elements_insert_stmt, element_values)
            conn.commit()

            self.dbapi.add_ions(elements_as_ions, conn=conn)

    # TODO Create a similar method to return atomic weight. This can probably
    # be abstracted to serve both atomic weight & atomic number.
    def get_atomic_nrs_map(
            self, symbols: str | list[str] = None, conn: Connection = None
    ) -> dict[str, int]:
        """
        Returns a dict of symbols mapped to their atomic numbers. If no atomic
        symbols are provided, a dict of all symbols and atomic numbers in the
        database is returned in ascending order of atomic number.
        """
        if isinstance(symbols, str):
            symbols = [symbols, ]

        with (nullcontext(conn) if conn else self.connect()) as conn:
            if symbols:
                get_stmt = (
                    select(self.element.c[ELEM_SYMBOL],
                           self.element.c[ATOMIC_NR])
                    .where(self.element.c[ELEM_SYMBOL].in_(symbols))
                )
            else:
                get_stmt = (
                    select(self.element.c[ELEM_SYMBOL],
                           self.element.c[ATOMIC_NR])
                    .order_by(self.element.c[ATOMIC_NR].asc())
                )

            get_res = conn.execute(get_stmt)
            return dict(get_res.t.all())

    def get_atomic_nrs(
            self, symbols: str | list[str] = None, conn: Connection = None
    ) -> list[int]:
        """
        Return a list of (or a single) atomic number, depending how many atomic
        symbols are provided as argument. If no atomic symbols are provided,
        all atomic numbers in the database are returned in ascending order.
        """
        atomic_nr_map = self.get_atomic_nrs_map(symbols, conn=conn)
        if symbols:
            atomic_nrs = [atomic_nr_map[sym] for sym in symbols]
            return atomic_nrs[0] if len(atomic_nrs) == 1 else atomic_nrs
        else:
            return [v for v in atomic_nr_map.values()]


def get_atomic_nr_for_symbol(
        db: PeriodicTableDBBuilder, symbol: str, conn: Connection = None
) -> int | None:
    """
    Get the atomic number of an element from its symbol.
    """
    atomic_nr_stmt = (
        select(db.element.c[ATOMIC_NR])
        .where(db.element.c[ELEM_SYMBOL] == symbol)
    )
    with (nullcontext(conn) if conn else db.connect()) as conn:
        atomic_nr_res = conn.execute(atomic_nr_stmt)
        return atomic_nr_res.scalar_one_or_none()


def get_weight_type_ids(
        db: PeriodicTableDBBuilder, conn: Connection = None
) -> dict[str, int]:
    """
    Returns a mapping of the name of the method used to determine/state the
    atomic weight of an element to its database id.
    """
    weight_type_ids_stmt = (
        select(db.atomic_weight_type.c.name, db.atomic_weight_type.c.id)
    )

    with (nullcontext(conn) if conn else db.connect()) as conn:
        weight_type_ids_res = conn.execute(weight_type_ids_stmt)
        return dict(weight_type_ids_res.t.all())


def get_none_weight_id(
        db: PeriodicTableDBBuilder, conn: Connection = None
) -> int:
    """
    Returns the database id of the atomic weight stated as "None".
    """
    none_weight_id_stmt = (
        select(db.atomic_weight, db.atomic_weight_type)
        .join(db.atomic_weight_type)
        .where(
            db.atomic_weight.c.weight == null(),
            db.atomic_weight_type.c.name == WEIGHT_TYPE_NONE
        )
    )

    with (nullcontext(conn) if conn else db.connect()) as conn:
        none_weight_id_res = conn.execute(none_weight_id_stmt)
        return none_weight_id_res.scalar_one()
