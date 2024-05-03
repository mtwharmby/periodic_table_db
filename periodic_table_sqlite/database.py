from sqlalchemy import (MetaData, Table, Column, Float, Integer, String,
                        ForeignKey, Engine, insert, select, Connection,
                        bindparam, null, or_)

from . import (
    Element,
    ATOMIC_NR, ELEM_SYMBOL, ELEM_NAME, ELEM_WEIGHT_ID, AT_WEIGHT,
    AT_WEIGHT_ESD, AT_WEIGHT_MIN, AT_WEIGHT_MAX, AT_WEIGHT_TYPE_ID,
    WEIGHT_TYPE_NONE, WEIGHT_TYPE_INTERVAL, WEIGHT_TYPE_REPORTED
)

metadata_obj = MetaData()

element = Table(
    "element",
    metadata_obj,
    Column(ATOMIC_NR, Integer, primary_key=True),
    Column(ELEM_SYMBOL, String, nullable=False, unique=True),
    Column(ELEM_NAME, String, nullable=False, unique=True),
    Column(ELEM_WEIGHT_ID, Integer, ForeignKey("atomic_weight.id"))
)

atomic_weight = Table(
    "atomic_weight",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column(AT_WEIGHT, Float, nullable=True, unique=True),
    # Null OK - no defined weight; we expect each element to have own weight
    Column(AT_WEIGHT_ESD, Float),
    Column(AT_WEIGHT_MIN, Float),
    Column(AT_WEIGHT_MAX, Float),
    Column(AT_WEIGHT_TYPE_ID, Integer, ForeignKey("atomic_weight_type.id"))
)

atomic_weight_type = Table(
    "atomic_weight_type",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("method", String, nullable=False),
    Column("reason", String, nullable=False)
)


def create_db(engine: Engine, metadata_obj: MetaData = metadata_obj):
    """
    Initialises the elements database.

    Adds the three methods used to determine/report atomic weights.
    """
    metadata_obj.create_all(engine)

    with engine.connect() as conn:
        # Create the options in the atomic weight type table
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
                          "of the interval; ESD is the difference between the "
                          "weight and either of the extrema of the interval."
            },
            {
                "name": WEIGHT_TYPE_REPORTED,
                "method": "reported",
                "reason": "CIAAW provides a best estimate for atomic mass, "
                          "based on the distribution of stable isotopes."
            }
        ]
        conn.execute(
            insert(atomic_weight_type), at_weight_values
        )
        conn.commit()


def get_weight_type_ids(conn: Connection) -> dict[str, int]:
    """
    Returns a mapping of the name of the method used to determine/state the
    atomic weight of an element to its database id.
    """
    weight_type_ids_stmt = (
        select(atomic_weight_type.c.name, atomic_weight_type.c.id)
    )
    weight_type_ids_res = conn.execute(weight_type_ids_stmt)
    weight_type_ids = [row._mapping for row in weight_type_ids_res]
    return {
        row["name"]: row["id"] for row in weight_type_ids
    }


def get_none_weight_id(conn: Connection) -> int:
    """
    Returns the database id of the atomic weight stated as "None".
    """
    none_weight_id_stmt = (
        select(atomic_weight, atomic_weight_type)
        .join(atomic_weight_type)
        .where(
            atomic_weight.c.weight == null(),
            atomic_weight_type.c.name == WEIGHT_TYPE_NONE
        )
    )
    none_weight_id_res = conn.execute(none_weight_id_stmt)
    return none_weight_id_res.scalar_one()


def add_elements(conn: Connection, elements: list[Element]):
    """
    Adds elements and their atomic weights to database, based on a list of
    elements supplied to the function.
    """
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
        select(atomic_weight_type.c.id)
        .where(atomic_weight_type.c.name == bindparam("weight_type"))
    )
    weights_insert_stmt = (
        insert(atomic_weight).values(weight_type_id=weight_type_subq)
    )
    conn.execute(weights_insert_stmt, weight_values)
    conn.commit()

    # Insert the elements
    # Use subquery to associate the weights with each element
    weight_subq = (
        select(atomic_weight.c.id)
        .join(atomic_weight_type)
        .where(
            atomic_weight_type.c.name == bindparam("weight_type"),
            or_(
                atomic_weight.c.weight == bindparam("weight"),
                atomic_weight.c.weight == null(),
            )
        )
    )
    # or_ statement needed above, since bindparam returns "col = None" rather
    # than "col IS NULL". This is a variation on this:
    #     https://stackoverflow.com/q/21668606
    # There's probably a neater solution using a TypeDecorator, but this works
    elements_insert_stmt = (
        insert(element).values(atomic_weight_id=weight_subq)
    )
    conn.execute(elements_insert_stmt, element_values)
    conn.commit()
