from typing import NamedTuple


def ensure_base_url(url: str) -> str:
    """
    Ensure that URL does not end with /

    :param url: URL
    """
    return url.removesuffix("/")


class AuthURLs(NamedTuple):
    authorize: str
    token: str
    userdata: str
