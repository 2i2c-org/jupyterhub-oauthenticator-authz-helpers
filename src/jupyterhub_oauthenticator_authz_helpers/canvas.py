mport aiohttp
import escapism  # type: ignore
import string
from collections.abc import Iterable
import urllib.parse


async def fetch_paginated_sequence(token: str, url: str) -> list:
    """
    Get paginated items from Canvas.

    https://developerdocs.instructure.com/services/canvas/basics/file.pagination
    """
    urls_to_fetch = [url]
    sequence = []

    async with aiohttp.ClientSession() as session:
        while urls_to_fetch:
            async with session.get(
                urls_to_fetch.pop(), headers={"Authorization": f"Bearer {token}"}
            ) as response:
                if response.status != 200:
                    raise Exception(
                        f"Error {response.status} while fetching items from {url}: {response.text()}"
                    )
                sequence.extend(await response.json())

                # Handle pagination
                try:
                    next_link = response.links["next"]
                except KeyError:
                    continue
                urls_to_fetch.append(str(next_link["url"]))

    return sequence


def ensure_valid_canvas_url(canvas_url: str) -> str:
    return canvas_url.removesuffix("/")


async def get_courses(canvas_url: str, token: str) -> list:
    """
    Get list of active courses for the current user.

    See https://canvas.instructure.com/doc/api/courses.html#method.courses.index
    """
    canvas_url = ensure_valid_canvas_url(canvas_url)
    url = f"{canvas_url}/api/v1/courses"

    return await fetch_paginated_sequence(token, url)


async def get_self_groups(canvas_url: str, token: str) -> list:
    """
    Get list of active groups for the current user.

    See https://canvas.instructure.com/doc/api/groups.html#method.groups.index
    """
    canvas_url = ensure_valid_canvas_url(canvas_url)
    url = f"{canvas_url}/api/v1/users/self/groups"

    return await fetch_paginated_sequence(token, url)


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
    canvas_courses: Iterable, canvas_course_key: str
) -> list:
    """
    Create group identifiers of the form

        course::<course-id>

    and

        course::<course-id>::enrollment_type::<enrollment-type>

    for each canvas group the user is a member of.

    :param self_groups: list of Canvas courses the user belongs to
    """
    groups = []

    for course in canvas_courses:
        course_id = course.get(canvas_course_key, None)
        if course_id is None:
            continue

        # Create the main course group
        groups.append(build_jupyterhub_group("course", course_id))

        # Create the enrollment groups
        # See https://canvas.instructure.com/doc/api/courses.html#method.courses.index
        for enrollment in course.get("enrollments", []):
            groups.append(
                build_jupyterhub_group(
                    "course", course_id, "enrollment_type", enrollment.get("type")
                )
            )

    return groups


def groups_from_canvas_groups(canvas_groups: Iterable) -> list:
    """
    Create group identifiers of the form

        <context-type>::<context-id>::group::<name>

    for each canvas group the user is a member of.

    See https://developerdocs.instructure.com/services/canvas/resources/groups.

    :param self_groups: list of Canvas groups the user belongs to
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



async def get_course_groups(
    canvas_url: str, token: str, canvas_course_key: str
) -> list:
    """
    Return a list of

        course::<course-id>

    and

        course::<course-id>::enrollment_type::<enrollment-type>

    group names generated from the courses and course enrollments that the user authenticated by
    the given token has access to.

    :param canvas_url: URL to Canvas instance
    :param token: authentication token granted by OAuth
    :param canvas_course_key: key in Course response that provides the course ID
    """
    courses = await get_courses(canvas_url, token)
    return groups_from_canvas_courses(courses, canvas_course_key)

get_course_groups.scopes = ["url:GET|/api/v1/courses"]


async def get_user_groups(canvas_url: str, token: str) -> list:
    """
    Return a list of

        <context-type>::<context-id>::group::<name>

    group names generated from the groups associated with the user authenticated by the given token.

    Access the .scopes attribute of this function to obtain the token scopes necessary to fulfil this request.

    :param canvas_url: URL to Canvas instance
    :param token: authentication token granted by OAuth
    """
    self_groups = await get_self_groups(canvas_url, token)
    return groups_from_canvas_groups(self_groups)

get_user_groups.scopes = ["url:GET|/api/v1/users/self/groups"]


# Base scopes needed for auth
def build_auth_urls(canvas_url: str) -> tuple[str, str]:
    """
    Return a tuple of the (token, auth) URLs for the given Canvas instance.
    """
    canvas_url = ensure_valid_canvas_url(canvas_url)
    return (
 
         f"{canvas_url}/login/oauth2/token",
         f"{canvas_url}/login/oauth2/auth"
            )

def build_profile_url(canvas_url: str) -> str:
    """
    Build the URL of the /users/self/profile endpoint URL for this Canvas instance.

    Access the .scopes attribute of this function to obtain the token scopes necessary to fulfil this request.

    """
    canvas_url = ensure_valid_canvas_url(canvas_url)
    return f"{canvas_url}/api/v1/users/self/profile"

build_profile_url.scopes = ["url:GET|/api/v1/users/:user_id/profile"]
