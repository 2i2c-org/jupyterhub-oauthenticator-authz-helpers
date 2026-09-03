"""
Helper routines for authorizing against Canvas instances.
"""

import string
from collections.abc import Iterable

import aiohttp
import escapism  # type: ignore

from .common import AuthURLs, BaseURL, ensure_base_url


async def fetch_canvas_resource(
    token: str, url: str, includes: list[str] | None = None
) -> list:
    """
    Get paginated items from Canvas.

    https://developerdocs.instructure.com/services/canvas/basics/file.pagination
    """
    sequence = []
    params = {"include": includes}

    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
                params=params,  # type: ignore
            ) as response:
                if response.status != 200:
                    raise RuntimeError(
                        f"Error {response.status} while fetching items from "
                        f"{url}: {response.text()}"
                    )
                sequence.extend(await response.json())

                # Handle pagination
                try:
                    next_link = response.links["next"]
                except KeyError:
                    break

                url = str(next_link["url"])

    return sequence


async def get_courses(canvas_url: BaseURL, token: str) -> list:
    """
    Get list of active courses for the current user.

    :param canvas_url: URL to Canvas instance
    :param token: Bearer token for authorization

    See https://canvas.instructure.com/doc/api/courses.html#method.courses.index.
    """
    url = f"{canvas_url}/api/v1/courses"

    return await fetch_canvas_resource(token, url, includes=["sections"])


async def get_self_groups(canvas_url: BaseURL, token: str) -> list:
    """
    Get list of active groups for the current user.

    :param canvas_url: URL to Canvas instance
    :param token: Bearer token for authorization

    See https://canvas.instructure.com/doc/api/groups.html#method.groups.index.
    """
    url = f"{canvas_url}/api/v1/users/self/groups"

    return await fetch_canvas_resource(token, url)


def escape_group_segment(segment: str) -> str:
    """
    Escape a group segment to protect against separators used in the group names

    :param segment: segment to escape
    """
    safe_chars = string.ascii_letters + string.digits + "@_-.+"
    return escapism.escape(segment, escape_char="&", safe=safe_chars)


def build_jupyterhub_group(*terms) -> str:
    """
    Return a group name assembled from provided terms.
    """
    return "::".join([escape_group_segment(str(t)) for t in terms])


def groups_from_canvas_courses(
    canvas_courses: Iterable,
    canvas_course_key: str,
    canvas_section_key: str,
) -> list:
    """
    Create group identifiers of the form

        course::<course>

    and

        course::<course>::enrollment_type::<enrollment-type>

    for each Canvas group the user is a member of.

    :param canvas_groups: list of Canvas Course resources
    :param canvas_course_key: key within Course response that defines the course ID
    :param canvas_section_key: key within Section response that defines the course ID
    """
    groups = []

    for course in canvas_courses:
        course_component = course.get(canvas_course_key, None)
        if course_component is None:
            continue

        # Create the main course group
        groups.append(build_jupyterhub_group("course", course_component))

        # Create the enrollment groups
        # See https://canvas.instructure.com/doc/api/courses.html#method.courses.index
        for enrollment in course.get("enrollments", []):
            groups.append(
                build_jupyterhub_group(
                    "course",
                    course_component,
                    "enrollment_type",
                    enrollment.get("type"),
                )
            )

        # Create the section groups
        for section in course.get("sections", []):
            section_component = section.get(canvas_section_key, None)
            if section_component is None:
                continue

            groups.append(
                build_jupyterhub_group(
                    "course", course_component, "section", section_component
                )
            )

    return groups


def groups_from_canvas_groups(canvas_groups: Iterable) -> list:
    """
    Create group identifiers of the form

        <context-type>::<context-id>::group::<group>

    for each Canvas group the user is a member of.

    See https://developerdocs.instructure.com/services/canvas/resources/groups.

    :param canvas_groups: list of Canvas Group resources
    """
    groups = set()

    for canvas_group in canvas_groups:
        if "name" not in canvas_group:
            continue

        group_name = canvas_group.get("name")
        # Determine group context, e.g. Account or Course
        context_type = canvas_group.get("context_type").lower()
        # Extract the corresponding ID of the context
        context_id = canvas_group[f"{context_type}_id"]
        groups.add(
            build_jupyterhub_group(context_type, context_id, "group", group_name)
        )

    return [*groups]


VALID_CANVAS_COURSE_KEYS = frozenset(
    {
        "id",
        "name",
        "sis_course_id",
        "uuid",
        "sis_import_id",
        "course_code",
        "original_name",
    }
)

VALID_CANVAS_SECTION_KEYS = frozenset(
    {
        "id",
        "name",
        "sis_section_id",
        "sis_import_id",
    }
)


async def get_course_groups(
    canvas_url: str,
    token: str,
    *,
    canvas_course_key: str = "name",
    canvas_section_key: str = "name",
) -> list:
    """
    Return a list of

        course::<course-id>

    and

        course::<course-id>::enrollment_type::<enrollment-type>

    group names generated from the courses and course enrollments that the user
    authenticated by the given token has access to.

    :param canvas_url: URL to Canvas instance
    :param token: authentication token granted by OAuth
    :param canvas_course_key: key in Course response that provides the course ID
    """
    if canvas_course_key not in VALID_CANVAS_COURSE_KEYS:
        raise ValueError(f"Invalid course key: {canvas_course_key!r}")

    if canvas_course_key not in VALID_CANVAS_SECTION_KEYS:
        raise ValueError(f"Invalid section key: {canvas_section_key!r}")

    courses = await get_courses(ensure_base_url(canvas_url), token)
    return groups_from_canvas_courses(courses, canvas_course_key, canvas_section_key)


get_course_groups.scopes = ["url:GET|/api/v1/courses"]  # type: ignore


async def get_user_groups(canvas_url: str, token: str) -> list:
    """
    Return a list of

        <context-type>::<context-id>::group::<name>

    group names generated from the groups associated with the user authenticated
    by the given token.

    Access the ``.scopes`` attribute of this function to obtain the token scopes
    necessary to fulfil this request.

    :param canvas_url: URL to Canvas instance
    :param token: authentication token granted by OAuth
    """
    self_groups = await get_self_groups(ensure_base_url(canvas_url), token)
    return groups_from_canvas_groups(self_groups)


get_user_groups.scopes = ["url:GET|/api/v1/users/self/groups"]  # type: ignore


# Base scopes needed for auth
def build_auth_urls(canvas_url: str) -> AuthURLs:
    """
    Return a named tuple of the ``(auth, token, userdata)`` URLs for the given
    Canvas instance.

    Examples
    --------
    >>> cfg = c.GenericOAuthenticator
    >>> cfg.authorize_url, cfg.token_url, cfg.userdata_url = build_auth_urls(canvas_url)

    :param canvas_url: URL to Canvas instance
    """
    canvas_url = ensure_base_url(canvas_url)
    return AuthURLs(
        f"{canvas_url}/login/oauth2/auth",
        f"{canvas_url}/login/oauth2/token",
        f"{canvas_url}/api/v1/users/self/profile",
    )


build_auth_urls.scopes = ["url:GET|/api/v1/users/:user_id/profile"]  # type: ignore
