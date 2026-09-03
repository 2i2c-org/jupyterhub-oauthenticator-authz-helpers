"""
Helper routines for authorizing against Mastodon instances.
"""

from collections.abc import Collection, Iterable
from typing import Any

import aiohttp

from .common import AuthURLs, BaseURL, ensure_base_url


async def get_relationships(
    mastodon_url: BaseURL, token: str, relationships: Iterable[str]
) -> list[str]:
    relationships_url = f"{mastodon_url}/api/v1/accounts/relationships"

    async with (
        aiohttp.ClientSession(headers={"Authorization": f"Bearer {token}"}) as session,
        session.get(
            relationships_url,
            params={"id[]": [*relationships]},
        ) as response,
    ):
        return await response.json()


async def get_followed_groups(
    mastodon_url: str, token: str, *, allow_list: dict[str, Any] | Collection[str]
) -> list[str]:
    """
    Get list of account IDs that are followed by the user identified by the given token,
    from a pre-determined allow-list of accounts.

    This security model assumes that each account in the allow-list has control over its
    follow requests.

    For example, if user "A" follows user "GPU" and user "HighCPU", they will be granted
    both groups.

    :param mastodon_url: URL to Mastodon instance
    :param token: Bearer token for authorization
    :param allow_list: collection of server account IDs representing distinct groups, or
    mapping from such IDs to user-friendly names, e.g. XXXXX → GPU

    See https://docs.joinmastodon.org/methods/accounts/#relationships.
    """
    if not isinstance(allow_list, dict):
        allow_list = {account_id: account_id for account_id in allow_list}

    relationships = await get_relationships(
        ensure_base_url(mastodon_url), token, allow_list.keys()
    )
    groups = []
    for item in relationships:
        if not item["following"]:
            continue

        account_id = item["id"]
        try:
            alias = allow_list[account_id]
        except KeyError:
            continue

        groups.append(f"following::{alias}")
    return groups


get_followed_groups.scopes = ["read:follows"]


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
