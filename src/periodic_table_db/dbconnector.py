from sqlalchemy import (
    MetaData, Connection, Engine,
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
