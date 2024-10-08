from contextlib import nullcontext
import logging

from sqlalchemy import (
    Engine, MetaData, Connection, insert, select, bindparam, update,
)

from ..db_builder import PeriodicTableDBBuilder
from ...shared import (
    ATOMIC_NR, E_SHELL_STRUCT, E_SUB_SHELL_STRUCT, PERIOD, GROUP, BLOCK,
    BLOCK_ID, LABEL, LABEL_ID
)
from .data import (
    groups as group_values, blocks as block_values, label_values
)
from .schema import (
    period_table, group_table, block_table, label_table, label_to_element_table
)
from .data import Atom

logger = logging.getLogger(__name__)


class ExtendedPeriodicTableDBBuilder(PeriodicTableDBBuilder):

    def __init__(self, engine: Engine, md: MetaData, **kwargs) -> None:
        super().__init__(engine, md, extended=True, kwargs=kwargs)

        self.period = period_table(self.metadata_obj, **kwargs)
        self.group = group_table(self.metadata_obj, **kwargs)
        self.block = block_table(self.metadata_obj, **kwargs)
        self.label = label_table(self.metadata_obj, **kwargs)
        self.label_element = label_to_element_table(
            self.metadata_obj, **kwargs
        )

    def _add_groups_blocks(self, conn: Connection = None):
        with (nullcontext(conn) if conn else self.connect()) as conn:
            logger.info(
                f"Adding group numbers, names and labels to {self.group.name} "
                "table."
            )
            conn.execute(insert(self.group), group_values)

            logger.info(
                f"Adding block names to {self.block.name} table."
            )
            conn.execute(insert(self.block), block_values)

            logger.info(
                f"Adding label names and descriptions to {self.label.name} "
                "table."
            )
            conn.execute(insert(self.label), label_values)

            conn.commit()

    def add_electronic_structure_data(
            self, atom_orbitals: Atom | list[Atom],
            conn: Connection = None
    ):
        if isinstance(atom_orbitals, Atom):
            atom_orbitals = [atom_orbitals, ]
        electronic_configs = [
            at.dict() for at in atom_orbitals
        ]

        with (nullcontext(conn) if conn else self.connect()) as conn:
            # Update entries in the Element table
            elem_values = [
                {
                    # Following needs to be different name to the column to
                    # avoid collision with bindparameter
                    "atomic_nr": config[ATOMIC_NR],
                    PERIOD: config[PERIOD],
                    GROUP: config[GROUP],
                    BLOCK: config[BLOCK]
                 } for config in electronic_configs
            ]
            block_subq = (
                select(self.block.c[BLOCK_ID])
                .where(self.block.c[BLOCK] == bindparam(BLOCK))
                .scalar_subquery()
            )
            elem_update_stmt = (
                update(self.element)
                .where(self.element.c[ATOMIC_NR] == bindparam("atomic_nr"))
                .values(block_id=block_subq)
            )
            logger.info(f"Updating {len(elem_values)} entries in "
                        f"{self.element.name} table with electronic "
                        "configuration.")
            conn.execute(elem_update_stmt, elem_values)

            # Update the entries in the Ion table
            ion_values = [
                {
                    "atomic_nr": config[ATOMIC_NR],
                    E_SHELL_STRUCT: config[E_SHELL_STRUCT],
                    E_SUB_SHELL_STRUCT: config[E_SUB_SHELL_STRUCT]
                } for config in electronic_configs
            ]

            ions_update_stmt = (
                update(self.ion)
                .where(self.ion.c[ATOMIC_NR] == bindparam("atomic_nr"))
            )
            logger.info(f"Updating {len(ion_values)} entries in "
                        f"{self.ion.name} table with electronic configuration."
                        )
            conn.execute(ions_update_stmt, ion_values)

            labels: list[dict[str, str | int]] = []
            for at in atom_orbitals:
                for lab in at.labels:
                    labels.append({
                        ATOMIC_NR: at.atomic_nr,
                        LABEL: lab
                    })

            if labels:
                label_subq = (
                    select(self.label.c[LABEL_ID])
                    .where(self.label.c[LABEL] == bindparam(LABEL))
                    .scalar_subquery()
                )
                label_maker_stmt = (
                    insert(self.label_element)
                    .values(label_id=label_subq)
                )
                logger.info(f"Adding {len(labels)} labels to the "
                            f"{self.label_element.name} table.")
                conn.execute(label_maker_stmt, labels)

            # Element and Ion table statements worked, so commit the changes
            conn.commit()
