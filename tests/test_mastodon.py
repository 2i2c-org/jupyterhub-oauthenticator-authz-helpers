import pytest

from jupyterhub_oauthenticator_authz_helpers.mastodon import (
    get_followed_groups,
    get_relationships,
)


@pytest.mark.asyncio
async def test_canvas_courses(mock_response):
    id_to_alias = {"1": "some-user", "2": "another-user"}

    with mock_response("mastodon", get_relationships):
        groups = await get_followed_groups("", "", id_to_alias)

    assert groups == [
        "following::some-user",
    ]
