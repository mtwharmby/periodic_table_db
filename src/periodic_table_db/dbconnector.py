from sqlalchemy import (
    MetaData, Connection, Engine, Table,
)


class DBConnector:

    def __init__(self, engine: Engine, md: MetaData):
        self.metadata_obj = md
        self.engine = engine

    def connect(self) -> Connection:
        """
        Calls the internal SQLalchemy Engine.connect() method.
        Convenience method.
        """
        return self.engine.connect()

    def get_tables_from_existing(
            self, table_names: list[str], prefix=""
    ) -> dict[str, Table]:
        self.metadata_obj.reflect(bind=self.engine)

        return {
            name: self.metadata_obj.tables[f"{prefix}{name}"]
            for name in table_names
        }
