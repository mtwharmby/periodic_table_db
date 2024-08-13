from sqlalchemy import (
    Column, Float, Integer, String, ForeignKey, Table, MetaData
)

from .shared import (
    ATOMIC_NR, ELEM_SYMBOL, AT_WEIGHT, ION_ID, ION_SYMBOL, ION_CHARGE,
    E_SHELL_STRUCT, E_SUB_SHELL_STRUCT, PERIOD, GROUP
)

TABLE_MAP = {
    "Element": "Element",
    "AtomicWeight": "AtomicWeight",
    "AtomicWeightType": "AtomicWeightType",
    "Ion": "Ion"
}


def element_table(
        metadata_obj: MetaData, extended: bool = False, prefix="", **kwargs
) -> Table:
    columns = [
        Column(ATOMIC_NR, Integer, primary_key=True),
        Column(ELEM_SYMBOL, String, nullable=False, unique=True),
        Column("name", String, nullable=False, unique=True),
        Column("atomic_weight_id", Integer, ForeignKey("AtomicWeight.id"))
    ]

    if extended:
        extra_cols = [
            Column(PERIOD, Integer, ForeignKey("Period.number")),
            Column(GROUP, Integer, ForeignKey("Group.number")),
            Column("block_id", Integer, ForeignKey("Block.id")),
        ]
        columns.extend(extra_cols)

    return Table(f"{prefix}{TABLE_MAP["Element"]}", metadata_obj, *columns)


def atomic_weight_table(metadata_obj: MetaData, prefix="", **kwargs) -> Table:
    return Table(
        f"{prefix}{TABLE_MAP["AtomicWeight"]}",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column(AT_WEIGHT, Float, nullable=True, unique=True),
        # Null OK - no defined weight
        Column(f"{AT_WEIGHT}_esd", Float),
        Column(f"{AT_WEIGHT}_min", Float),
        Column(f"{AT_WEIGHT}_max", Float),
        Column("weight_type_id", Integer, ForeignKey("AtomicWeightType.id"))
    )


def atomic_weight_type_table(
        metadata_obj: MetaData, prefix="", **kwargs
) -> Table:
    return Table(
        f"{prefix}{TABLE_MAP["AtomicWeightType"]}",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("name", String, nullable=False),
        Column("method", String, nullable=False),
        Column("reason", String, nullable=False)
    )


def ions_table(
        metadata_obj: MetaData, extended: bool = False, prefix="", **kwargs
) -> Table:
    columns = [
        Column(ION_ID, Integer, primary_key=True),
        Column(ION_SYMBOL, String, nullable=False),
        Column(ION_CHARGE, Integer, nullable=False),
        Column(ATOMIC_NR, Integer, ForeignKey(f"Element.{ATOMIC_NR}"))
    ]

    if extended:
        extra_cols = [
            Column(E_SHELL_STRUCT, String, nullable=True),
            Column(E_SUB_SHELL_STRUCT, String, nullable=True)
        ]
        columns.extend(extra_cols)

    return Table(f"{prefix}{TABLE_MAP["Ion"]}", metadata_obj, *columns)
