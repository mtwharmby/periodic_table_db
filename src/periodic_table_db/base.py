from sqlalchemy import (
    Column, Float, Integer, String, ForeignKey, Table, MetaData
)

from . import (
    ATOMIC_NR, ELEM_SYMBOL, ELEM_NAME, ELEM_WEIGHT_ID, AT_WEIGHT,
    AT_WEIGHT_ESD, AT_WEIGHT_MIN, AT_WEIGHT_MAX, AT_WEIGHT_TYPE_ID,
)


def element_table(metadata_obj: MetaData, extended: bool = False) -> Table:
    columns = [
        Column(ATOMIC_NR, Integer, primary_key=True),
        Column(ELEM_SYMBOL, String, nullable=False, unique=True),
        Column(ELEM_NAME, String, nullable=False, unique=True),
        Column(ELEM_WEIGHT_ID, Integer, ForeignKey("AtomicWeight.id"))
    ]

    if extended:
        pass
        # group, period, block (others?)
        # columns.append()

    return Table("Element", metadata_obj, *columns)


def atomic_weight_table(metadata_obj: MetaData) -> Table:
    return Table(
        "AtomicWeight",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column(AT_WEIGHT, Float, nullable=True, unique=True),
        # Null OK - no defined weight
        Column(AT_WEIGHT_ESD, Float),
        Column(AT_WEIGHT_MIN, Float),
        Column(AT_WEIGHT_MAX, Float),
        Column(AT_WEIGHT_TYPE_ID, Integer, ForeignKey("AtomicWeightType.id"))
    )


def atomic_weight_type_table(metadata_obj: MetaData) -> Table:
    return Table(
        "AtomicWeightType",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("name", String, nullable=False),
        Column("method", String, nullable=False),
        Column("reason", String, nullable=False)
    )
