from typing import NamedTuple, NewType, cast

BaseURL = NewType("BaseURL", str)


def ensure_base_url(url: str) -> BaseURL:
    """
    Ensure that URL does not end with /

    :param url: URL
    """
    return cast(BaseURL, url.removesuffix("/"))


class AuthURLs(NamedTuple):
    authorize: str
    token: str
    userdata: str
