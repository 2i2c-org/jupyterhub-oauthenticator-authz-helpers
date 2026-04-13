import pytest

from jupyterhub_oauthenticator_authz_helpers.canvas import (
    get_course_groups,
    get_courses,
    get_self_groups,
    get_user_groups,
)


@pytest.mark.asyncio
async def test_canvas_courses(mock_response):
    with mock_response("canvas", get_courses):
        groups = await get_course_groups("", "", "course_code")

    assert groups == [
        "course::2i2c-jupyter",
        "course::2i2c-jupyter::enrollment_type::teacher",
    ]


@pytest.mark.asyncio
async def test_canvas_users(mock_response):
    with mock_response("canvas", get_self_groups):
        groups = await get_user_groups("", "")

    assert groups == ["course::3::group::Math&20Group&201"]
