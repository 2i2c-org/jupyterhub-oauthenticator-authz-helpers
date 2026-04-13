import contextlib
import json
import pathlib
import unittest.mock

import pytest

TEST_FILES = pathlib.Path(__file__).parent / "responses"


@pytest.fixture
def mock_response():
    @contextlib.contextmanager
    def impl(group, func):
        name = f"{func.__module__}.{func.__qualname__}"
        with (
            unittest.mock.patch(name) as impl,
            (TEST_FILES / group / f"{func.__qualname__}.json").open() as f,
        ):
            impl.return_value = json.load(f)
            yield

    return impl
