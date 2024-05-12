import logging

from sqlalchemy import (
    MetaData, insert, select, Connection, bindparam, null, or_, Engine,
)

from . import (
    Element, WEIGHT_TYPE_NONE, WEIGHT_TYPE_INTERVAL, WEIGHT_TYPE_REPORTED
)
from .schema import (
    element_table, atomic_weight_table, atomic_weight_type_table
)

logger = logging.getLogger(__name__)


class PeriodicTableDBBase:

    def __init__(self, engine: Engine, md: MetaData, extended=False) -> None:
        self.metadata_obj = md
        self.engine = engine
        self.element = element_table(self.metadata_obj, extended=extended)
        self.atomic_weight = atomic_weight_table(self.metadata_obj)
        self.atomic_weight_type = atomic_weight_type_table(self.metadata_obj)

    def create_db(self):
        """
        Initialises the elements database.

        Adds the three methods used to determine/report atomic weights.
        """
        logger.info("Initialising database.")
        self.metadata_obj.create_all(self.engine)

        with self.engine.connect() as conn:
            self.add_atomic_weight_types(conn)

    def add_atomic_weight_types(self, conn: Connection):
        """
        Create the constants in the atomic weight type table.
        """
        # TODO Move these to new data module
        at_weight_values = [
            {
                "name": WEIGHT_TYPE_NONE,
                "method": "none",
                "reason": "No stable isotope(s) with characteristic isotopic "
                          "composition exist. A standard atomic weight cannot "
                          "be determined."
            },
            {
                "name": WEIGHT_TYPE_INTERVAL,
                "method": "calculated",
                "reason": "CIAAW expresses atomic weight as an interval "
                          "intended to encompass all \"normal\" materials. "
                          "Atomic weight has been calculated as the midpoint "
                          "of the interval; uncertainty is calculated as half "
                          "the difference between the maximum and minimum of "
                          "the interval."
            },
            {
                "name": WEIGHT_TYPE_REPORTED,
                "method": "tabulated",
                "reason": "CIAAW provides a single value for the atomic "
                          "weight with an uncertainty. The quoted atomic "
                          "weight is representative of the population of a "
                          "sample of atoms of the element. A minimum and "
                          "maximum weight have been calculated from the "
                          "uncertainty."
            }
        ]
        logger.info(
            f"Adding weight types to {self.atomic_weight_type.name} table."
        )
        conn.execute(
            insert(self.atomic_weight_type), at_weight_values
        )
        conn.commit()

    def add_elements(self, elements: list[Element]):
        """
        Adds elements and their atomic weights to database, based on a list of
        elements supplied to the function.
        """
        with self.engine.connect() as conn:
            element_values = []
            weight_values = []

            for elem in elements:
                el = elem.dict()
                weight = el.pop("weight")
                el["weight"] = weight["weight"]
                el["weight_type"] = weight["weight_type"]
                element_values.append(el)
                if weight not in weight_values:
                    weight_values.append(weight)

            # Insert the atomic weights
            # Use subquery to associate weight types with each weight
            weight_type_subq = (
                select(self.atomic_weight_type.c.id)
                .where(self.atomic_weight_type.c.name
                       == bindparam("weight_type"))
            )
            weights_insert_stmt = (
                insert(self.atomic_weight)
                .values(weight_type_id=weight_type_subq)
            )
            logger.info(f"Adding {len(weight_values)} atomic weight entries "
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
                )
            )
            # or_ statement needed above, since bindparam returns "col = None"
            # rather than "col IS NULL". This is a variation on this:
            #     https://stackoverflow.com/q/21668606
            # There's probably a neater solution using a TypeDecorator, but
            # this works
            elements_insert_stmt = (
                insert(self.element).values(atomic_weight_id=weight_subq)
            )
            logger.info(f"Adding {len(element_values)} element entries to "
                        f"{self.element.name} table.")
            conn.execute(elements_insert_stmt, element_values)
            conn.commit()


def get_weight_type_ids(
        db: PeriodicTableDBBase, conn: Connection
        ) -> dict[str, int]:
    """
    Returns a mapping of the name of the method used to determine/state the
    atomic weight of an element to its database id.
    """
    weight_type_ids_stmt = (
        select(db.atomic_weight_type.c.name, db.atomic_weight_type.c.id)
    )
    weight_type_ids_res = conn.execute(weight_type_ids_stmt)
    weight_type_ids = [row._mapping for row in weight_type_ids_res]
    return {
        row["name"]: row["id"] for row in weight_type_ids
    }


def get_none_weight_id(db: PeriodicTableDBBase, conn: Connection) -> int:
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
    none_weight_id_res = conn.execute(none_weight_id_stmt)
    return none_weight_id_res.scalar_one()
