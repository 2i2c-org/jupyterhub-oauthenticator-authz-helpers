import pytest

from jupyterhub_oauthenticator_authz_helpers.canvas import (
    get_course_groups,
    get_courses,
    get_self_groups,
    get_user_groups,
)


@pytest.mark.asyncio
async def test_canvas_courses_default(mock_response):
    with mock_response("canvas", get_courses):
        groups = await get_course_groups("", "")

    assert groups == [
        "course::2i2c&20JupyterHub&20Integration&20Testing",
        "course::2i2c&20JupyterHub&20Integration&20Testing::enrollment_type::teacher",
    ]


@pytest.mark.asyncio
async def test_canvas_courses_code(mock_response):
    with mock_response("canvas", get_courses):
        groups = await get_course_groups("", "", canvas_course_key="course_code")

    assert groups == [
        "course::2i2c-jupyter",
        "course::2i2c-jupyter::enrollment_type::teacher",
    ]


@pytest.mark.asyncio
async def test_canvas_courses_id(mock_response):
    with mock_response("canvas", get_courses):
        groups = await get_course_groups("", "", canvas_course_key="id")

    assert groups == [
        "course::3248",
        "course::3248::enrollment_type::teacher",
    ]


@pytest.mark.asyncio
async def test_canvas_users(mock_response):
    with mock_response("canvas", get_self_groups):
        groups = await get_user_groups("", "")

    assert groups == ["course::3::group::Math&20Group&201"]


# Now test setions
@pytest.mark.asyncio
async def test_canvas_sections_default(mock_response):
    with mock_response("canvas_sections", get_courses):
        groups = await get_course_groups("", "")

    assert groups == [
        # Check that the default groups are there
        "course::2i2c&20JupyterHub&20Integration&20Testing",
        "course::2i2c&20JupyterHub&20Integration&20Testing::enrollment_type::teacher",
        # Test the name of section
        "course::2i2c&20JupyterHub&20Integration&20Testing::section::2i2c&20Jupyter&20Test&20Course",
    ]


@pytest.mark.asyncio
async def test_canvas_sections_id(mock_response):
    with mock_response("canvas_sections", get_courses):
        groups = await get_course_groups("", "", canvas_section_key="id")

    assert groups == [
        "course::2i2c&20JupyterHub&20Integration&20Testing",
        "course::2i2c&20JupyterHub&20Integration&20Testing::enrollment_type::teacher",
        "course::2i2c&20JupyterHub&20Integration&20Testing::section::476176",
    ]
