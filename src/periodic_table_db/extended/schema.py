from sqlalchemy import (
    Column, Integer, String, ForeignKey, Table, MetaData
)

from .. import ATOMIC_NR


def period_table(metadata_obj: MetaData) -> Table:
    return Table(
        "Period",
        metadata_obj,
        Column("number", Integer, primary_key=True)
    )


def group_table(metadata_obj: MetaData) -> Table:
    return Table(
        "Group",
        metadata_obj,
        Column("number", Integer, primary_key=True),
        Column("label_eu", String, nullable=False),
        Column("label_us", String, nullable=False),
        Column("name", String, nullable=True),
    )


def block_table(metadata_obj: MetaData) -> Table:
    return Table(
        "Block",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("block", String, nullable=False)
    )


def label_table(metadata_obj: MetaData) -> Table:
    return Table(
        "Label",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("name", String, nullable=False),
        Column("description", String, nullable=True)
    )


def label_to_element_table(metadata_obj: MetaData) -> Table:
    return Table(
        "ElementLabel",
        metadata_obj,
        Column("label_id", Integer, ForeignKey("Label.id"), primary_key=True),
        Column(ATOMIC_NR, Integer, ForeignKey(f"Element.{ATOMIC_NR}"),
               primary_key=True),
    )
