from pathlib import Path

from periodic_table_db.builder import generatedb
from periodic_table_db.dbapi import PeriodicTableDBAPI

from tests.resources.requests_local_file import LocalFileAdapter


def test_generate_db():
    at_weights = Path("./tests/test_files/atomic-weights.htm")
    at_weights_url = at_weights.resolve().as_uri()
    cfg = ("file://", LocalFileAdapter())

    pt_dbapi = generatedb.generate_db(interactive=False, extended=True,
                                      url=at_weights_url, adapter_cfg=cfg)

    assert isinstance(pt_dbapi, PeriodicTableDBAPI)
