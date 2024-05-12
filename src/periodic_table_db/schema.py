from sqlalchemy import (
    Column, Float, Integer, String, ForeignKey, Table, MetaData
)

from .shared import (
    ATOMIC_NR, ELEM_SYMBOL, ELEM_NAME, ELEM_WEIGHT_ID, AT_WEIGHT,
    AT_WEIGHT_ESD, AT_WEIGHT_MIN, AT_WEIGHT_MAX, AT_WEIGHT_TYPE_ID,
    ION_ID, ION_SYMBOL, ION_CHARGE,
)


def element_table(
        metadata_obj: MetaData, extended: bool = False, prefix="", **kwargs
        ) -> Table:
    columns = [
        Column(ATOMIC_NR, Integer, primary_key=True),
        Column(ELEM_SYMBOL, String, nullable=False, unique=True),
        Column(ELEM_NAME, String, nullable=False, unique=True),
        Column(ELEM_WEIGHT_ID, Integer, ForeignKey("AtomicWeight.id"))
    ]

    if extended:
        extra_cols = [
            Column("period", Integer, ForeignKey("Period.number")),
            Column("group", Integer, ForeignKey("Group.number")),
            Column("block_id", Integer, ForeignKey("Block.id")),
        ]
        columns.extend(extra_cols)

    return Table(f"{prefix}Element", metadata_obj, *columns)


def atomic_weight_table(metadata_obj: MetaData, prefix="", **kwargs) -> Table:
    return Table(
        f"{prefix}AtomicWeight",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column(AT_WEIGHT, Float, nullable=True, unique=True),
        # Null OK - no defined weight
        Column(AT_WEIGHT_ESD, Float),
        Column(AT_WEIGHT_MIN, Float),
        Column(AT_WEIGHT_MAX, Float),
        Column(AT_WEIGHT_TYPE_ID, Integer, ForeignKey("AtomicWeightType.id"))
    )


def atomic_weight_type_table(
        metadata_obj: MetaData, prefix="", **kwargs
        ) -> Table:
    return Table(
        f"{prefix}AtomicWeightType",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("name", String, nullable=False),
        Column("method", String, nullable=False),
        Column("reason", String, nullable=False)
    )


def ions_table(metadata_obj: MetaData, prefix="", **kwargs) -> Table:
    return Table(
        f"{prefix}Ion",
        metadata_obj,
        Column(ION_ID, Integer, primary_key=True),
        Column(ION_SYMBOL, String, nullable=False),
        Column(ION_CHARGE, Integer, nullable=False),
        Column(ATOMIC_NR, Integer, ForeignKey(f"Element.{ATOMIC_NR}"))
    )
