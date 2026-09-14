from typing import NamedTuple

from yarl import URL


def ensure_base_url(url: str) -> URL:
    """
    Ensure that URL does not end with /

    :param url: URL
    """
    return URL(url.removesuffix("/"))


class AuthURLs(NamedTuple):
    authorize: str
    token: str
    userdata: str
