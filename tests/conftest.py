import os
import tempfile
# import warnings

import pytest

from sas_select import create_app
from sas_select.db import get_db
from sas_select.datasheet import empty_tbl_products

# read in SQL for populating test data
with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    data_sql: str = f.read().decode("utf8")


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    # warnings.warn(UserWarning("db in file: " + db_path))
    # create the app with common test config
    app = create_app({"TESTING": True, "DATABASE": db_path})

    # create the database and load test data
    with app.app_context():
        empty_tbl_products()
        get_db().executescript(data_sql)

    yield app

    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()
