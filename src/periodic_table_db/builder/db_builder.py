import logging
from contextlib import nullcontext

from sqlalchemy import (
    MetaData, insert, select, Connection, bindparam, null, or_, Engine,
)

from ..dbconnector import DBConnector
from ..dbapi import PeriodicTableDBAPI
from .shared import Element
from ..shared import Ion, ION_ID
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
                ion = Ion(
                    element_symbol=elem.symbol,
                    charge=0,
                    valence_state=False,
                    atomic_number=elem.atomic_number,)
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
