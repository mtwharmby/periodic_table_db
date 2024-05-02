import logging
from pathlib import Path
import sys

from sqlalchemy import create_engine

from periodic_table_sqlite.database import create_db, add_elements
from periodic_table_sqlite.www_table_parser import parse_table


logger = logging.getLogger(__name__)


def main(db_path: Path = None, interactive: bool = True):
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


if __name__ == "__main__":
    main(interactive=False)
