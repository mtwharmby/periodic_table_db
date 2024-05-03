import argparse
import logging
from pathlib import Path
import sys

from sqlalchemy import create_engine

from periodic_table_sqlite.database import create_db, add_elements
from periodic_table_sqlite.www_table_parser import parse_table


logger = logging.getLogger(__name__)


def generate_db(db_path: Path = None, interactive: bool = True):
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

    # Initialise the database
    engine = create_engine(db_url)
    create_db(engine)

    # Get elements from CIAAW website...
    elements = parse_table()
    # ... and put them in the database
    with engine.connect() as conn:
        add_elements(conn, elements)


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
            help="Enable debug log output"
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

    generate_db(interactive=interactive, **kwargs)


if __name__ == "__main__":
    main(interactive=True)
