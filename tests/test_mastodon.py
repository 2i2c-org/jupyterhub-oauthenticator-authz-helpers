import pytest

from jupyterhub_oauthenticator_authz_helpers.mastodon import (
    get_followed_groups,
    get_relationships,
)


@pytest.mark.asyncio
async def test_mastodon_courses_remap(mock_response):
    id_to_alias = {"1": "some-user", "2": "another-user"}

    with mock_response("mastodon", get_relationships):
        groups = await get_followed_groups("", "", allow_list=id_to_alias)

    assert groups == [
        "following::some-user",
    ]


@pytest.mark.asyncio
async def test_mastodon_courses(mock_response):
    allow_list = ["1", "2"]

    with mock_response("mastodon", get_relationships):
        groups = await get_followed_groups("", "", allow_list=allow_list)

    assert groups == [
        "following::1",
    ]
