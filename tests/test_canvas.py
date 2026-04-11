import contextlib
import pytest
import json
import pathlib
import pytest_asyncio
import unittest.mock

from jupyterhub_oauthenticator_authz_helpers.canvas import (
    get_courses,
    get_self_groups,
    # Exported functions
    get_course_groups,
    get_user_groups,
)


TEST_FILES = pathlib.Path(__file__).parent / "responses"


@contextlib.contextmanager
def mock_response(func):
    name = f"{func.__module__}.{func.__qualname__}"
    with (
        unittest.mock.patch(name) as impl,
        (TEST_FILES / f"{func.__qualname__}.json").open() as f,
    ):
        impl.return_value = json.load(f)
        yield


@pytest.mark.asyncio
async def test_canvas_courses():
    with mock_response(get_courses):
        groups = await get_course_groups("", "", "course_code")

    assert groups == [
        "course::2i2c-jupyter",
        "course::2i2c-jupyter::enrollment_type::teacher",
    ]


@pytest.mark.asyncio
async def test_canvas_users():
    with mock_response(get_self_groups):
        groups = await get_user_groups("", "")

    assert groups == [
        "course::3::group::Math&20Group&201",
    ]
