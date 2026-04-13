"""
Helper routines for authorizing against Mastodon instances.
"""

from collections.abc import Iterable
from typing import Any, NamedTuple

import aiohttp

from .utils import ensure_base_url


async def get_relationships(
    mastodon_url: str, token: str, relationships: Iterable[str]
) -> list[str]:
    mastodon_url = ensure_base_url(mastodon_url)
    relationships_url = f"{mastodon_url}/api/v1/accounts/relationships"

    async with aiohttp.ClientSession(
        headers={"Authorization": f"Bearer {token}"}
    ) as session:
        async with session.get(
            relationships_url,
            params={"id[]": [*relationships]},
        ) as response:
            return await response.json()


async def get_followed_groups(
    mastodon_url: str, token: str, id_to_group_name: dict[str, Any]
) -> list[str]:
    """
    Get list of account IDs that are followed by the user identified by the given token
    from a pre-determined allow-list of accounts.

    :param mastodon_url: URL to Mastodon instance
    :param token: Bearer token for authorization
    :param id_to_group_name: mapping from permitted Mastodon server account IDs to
                             user-friendly names

    See https://docs.joinmastodon.org/methods/accounts/#relationships.
    """
    relationships = await get_relationships(
        mastodon_url, token, id_to_group_name.keys()
    )
    groups = []
    for item in relationships:
        if not item["following"]:
            continue

        account_id = item["id"]
        try:
            alias = id_to_group_name[account_id]
        except KeyError:
            continue

        groups.append(f"following::{alias}")
    return groups


get_followed_groups.scopes = ["read:follows"]


class AuthURLs(NamedTuple):
    authorize: str
    token: str
    userdata: str


# Base scopes needed for auth
def build_auth_urls(mastodon_url: str) -> AuthURLs:
    """
    Return a named tuple of the ``(auth, token, userdata)`` URLs for the given
    Mastodon instance.

    Examples
    --------
    >>> cfg = c.GenericOAuthenticator
    >>> cfg.authorize_url, cfg.token_url, cfg.userdata_url = build_auth_urls(mastodon_url)  # noqa: B950

    :param canvas_url: URL to Mastodon instance
    """
    mastodon_url = ensure_base_url(mastodon_url)
    return AuthURLs(
        f"{mastodon_url}/oauth/authorize",
        f"{mastodon_url}/oauth/token",
        f"{mastodon_url}/api/v1/accounts/verify_credentials",
    )


build_auth_urls.scopes = ["read:accounts"]
