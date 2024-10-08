import argparse
import logging
from pathlib import Path
import sys

from sqlalchemy import MetaData, Engine, create_engine

# Absolute imports here so that debugging can be run
from periodic_table_db.builder import PeriodicTableDBBuilder
from periodic_table_db.builder.features import get_elements
from periodic_table_db.builder.extended import (
    ExtendedPeriodicTableDBBuilder
)
from periodic_table_db.builder.extended.features import (
    get_electronic_structure, add_labels
)


logger = logging.getLogger(__name__)


def get_db_url(db_path: Path | None, interactive: bool):
    if db_path:
        db_path = db_path.resolve()
        if db_path.exists():
            if interactive:
                try:
                    input(f"A file with the name {db_path} already exists. "
                          "Press enter to delete or Ctrl+C to cancel.")
                except KeyboardInterrupt:
                    print("Cancelled.")
                    sys.exit(0)
            logger.warning(f"Deleting existing file at {db_path}")

            db_url = f"sqlite:///{db_path}"
    else:
        db_url = "sqlite:///:memory:"

    return db_url


def construct_db(
        engine: Engine, md: MetaData, extended: bool, **kwargs: dict
) -> PeriodicTableDBBuilder:
    # Initialise the database
    pt_db = (
        ExtendedPeriodicTableDBBuilder(engine, md) if extended
        else PeriodicTableDBBuilder(engine, md)
    )
    pt_db.create_db()

    # Get elements from CIAAW website...
    elements = get_elements(**kwargs)
    # ... and put them in the database
    pt_db.add_elements(elements)

    if extended:
        pt_db._add_groups_blocks()
        electronic_configs = get_electronic_structure(elements)
        add_labels(electronic_configs)
        pt_db.add_electronic_structure_data(electronic_configs)

    return pt_db.dbapi


def generate_db(
        db_path: Path | None = None, interactive: bool = True,
        extended: bool = True, **kwargs: dict
):
    db_url = get_db_url(db_path, interactive)
    engine = create_engine(db_url)
    metadata_obj = MetaData()
    return construct_db(engine, metadata_obj, extended, **kwargs)


def main(interactive=True):
    logging.basicConfig(level=logging.INFO)
    kwargs = {}

    if interactive:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--db-path", type=Path,
            help="Directory where periodic table SQLite database file will be "
                 "created."
        )
        parser.add_argument(
            "--debug", action="store_true",
            help="Enable debug log output."
        )
        parser.add_argument(
            "--extended", action="store_true",
            help="Enable extended database features."
        )

        args = parser.parse_args()

        if args.db_path:
            if args.db_path.exists() and args.db_path.is_dir():
                db_path: Path = args.db_path / "periodic_table.sqlite"
                kwargs["db_path"] = db_path
            else:
                print(f"ERROR: Path '{args.db_path}' does not exist or is "
                      "not a directory.\n")
                sys.exit(1)

        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)

        if args.extended:
            kwargs["extended"] = True

    generate_db(interactive=interactive, **kwargs)


if __name__ == "__main__":
    main(interactive=True)
