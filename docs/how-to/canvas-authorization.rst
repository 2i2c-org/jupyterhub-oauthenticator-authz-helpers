Set Up Canvas Authorization
===========================

.. epigraph::

   Authentication [...] is the function of specifying rights/privileges for accessing resources.

   -- `Wikipedia <https://en.wikipedia.org/wiki/Authorization>`__

Having :doc:`set up authentication with Canvas<canvas-authentication>`, we must now configure the hub to permit or deny particular users. This falls under the topic of "authorization". JupyterHub has several authorization mechanisms:

* :py:attr:`allowed_users <oauthenticator.generic.GenericOAuthenticator.allowed_users>`
* :py:attr:`allowed_groups <oauthenticator.generic.GenericOAuthenticator.allowed_groups>`
* :py:attr:`allowed_scopes <oauthenticator.generic.GenericOAuthenticator.allowed_scopes>`
* :py:attr:`allow_all <oauthenticator.generic.GenericOAuthenticator.allow_all>`

If :py:attr:`allow_all <oauthenticator.generic.GenericOAuthenticator.allow_all>` is set, then any user that is authenticated can log in to the hub. Otherwise, the remaining authorization mechanisms can be used to restrict access to specific users, or *kinds* of users. For our purposes, we will not be using :py:attr:`allowed_scopes <oauthenticator.generic.GenericOAuthenticator.allowed_scopes>` [#scopes]_.

Add a hook to modify the authorization state
--------------------------------------------

To determine whether a user should be able to log in to a JupyterHub, we're asking the following question:

  Is user ``user-x`` authorized to access resource ``resource-y``?

let us slightly restate this question:

  Users in ``group-y`` are allowed to access ``resource-y``. Is ``user-x`` a member of ``group-y``?

Clearly, if we can identify which *groups* each user belongs to, we can then determine whether they are *authorized* to access the hub. Canvas provides various kinds of group-like concepts, such as *courses*, *course roles*, *sections*, and *user groups*. Before we chose from this list, let us first add a `modify_auth_state_hook` that we will use to populate a special ``auth-state`` key with the names of JupyterHub groups that the user is considered a member of.

.. code-block:: python
   :emphasize-lines: 13-27

   from jupyterhub_oauthenticator_authz_helpers import build_auth_urls

   canvas_url = "<CANVAS-URL>"

   cfg = c.GenericOAuthenticator

   # Configure auth and token URLs
   cfg.authorize_url, cfg.token_url, cfg.userdata_url = build_auth_urls(canvas_url)

   # Scopes that this token will need
   cfg.scope = build_auth_urls.scopes

   # Define auth-state hook
   async def auth_state_hook(authenticator, auth_state):
     if auth_state is None:
       return None

     # TODO: implement this logic
     return auth_state

   cfg.modify_auth_state_hook = modify_auth_state_hook

Configuring group membership from courses
-----------------------------------------

Let's start by using the Canvas *courses* that the user belongs to as a proxy for the JupyterHub *groups* that they are members of. We'll use the :py:func:`get_course_groups <jupyterhub_oauthenticator_authz_helpers.canvas.get_course_groups>` function. In addition to *using* this function to compute the groups, we also need to request the necessary scopes, and configure JupyterHub to look for the computed groups once we've stored them in the ``auth_state`` dictionary:

.. code-block:: python
   :emphasize-lines: 1,11,13-14,21-22

   from jupyterhub_oauthenticator_authz_helpers import build_auth_urls, get_course_groups

   canvas_url = "<CANVAS-URL>"

   cfg = c.GenericOAuthenticator

   # Configure auth and token URLs
   cfg.authorize_url, cfg.token_url, cfg.userdata_url = build_auth_urls(canvas_url)

   # Scopes that this token will need
   cfg.scope = build_auth_urls.scopes + get_course_groups.scopes

   # Store/retrieve group information from "groups"
   cfg.auth_state_groups_key = "groups"

   # Define auth-state hook
   async def auth_state_hook(authenticator, auth_state):
     if auth_state is None:
       return None

     # Populate JupyterHub groups with names from Canvas course and sections
     auth_state[authenticator.auth_state_groups_key] = await get_course_groups(canvas_url, auth_state["access_token"])

     return auth_state

   cfg.modify_auth_state_hook = modify_auth_state_hook

If the user is a member of a group called "JupyterHub Users", and a section called "Climate Research", they would be enrolled in the following JupyterHub groups:

* ``course::JupyterHub&20Users``
* ``course::JupyterHub&20Users::section::Climate&20Research``

Whitespace and other complex punctuation (outside of the letters, numbers, and ``@_-.+`` characters) are escaped with the `&` symbol using a reversible escapement algorithm. If users have particular privileges within a course, this is also represented via a group. For example, if the user is a "Teacher" of the aforementioned course, they would also have the following group:

* ``course::2i2c&20JupyterHub&20Integration&20Testing::enrollment_type::teacher``

We can alternatively use the course code, which is designed for unique IDs:

.. code-block:: python
   :emphasize-lines: 25

   from jupyterhub_oauthenticator_authz_helpers import build_auth_urls, get_course_groups

   canvas_url = "<CANVAS-URL>"

   cfg = c.GenericOAuthenticator

   # Configure auth and token URLs
   cfg.authorize_url, cfg.token_url, cfg.userdata_url = build_auth_urls(canvas_url)

   # Scopes that this token will need
   cfg.scope = build_auth_urls.scopes + get_course_groups.scopes

   # Store/retrieve group information from "groups"
   cfg.auth_state_groups_key = "groups"

   # Define auth-state hook
   async def auth_state_hook(authenticator, auth_state):
     if auth_state is None:
       return None

     # Populate JupyterHub groups with names from Canvas course and sections
     auth_state[authenticator.auth_state_groups_key] = await get_course_groups(
       canvas_url,
       auth_state["access_token"],
       canvas_course_key="course_code",
     )

     return auth_state

   cfg.modify_auth_state_hook = modify_auth_state_hook

See the :py:func:`get_course_groups <jupyterhub_oauthenticator_authz_helpers.canvas.get_course_groups>` documentation for more details.

Allow specific groups to log in to the hub
---------------------------------------------------

Now that we have associated users with JupyterHub groups derived from their Canvas metadata, we can instruct the hub to grant them log-in access. We can also grant teachers with *admin* privileges:

.. code-block:: python
   :emphasize-lines: 28-29,31-32

   from jupyterhub_oauthenticator_authz_helpers import build_auth_urls, get_course_groups

   canvas_url = "<CANVAS-URL>"

   cfg = c.GenericOAuthenticator

   # Configure auth and token URLs
   cfg.authorize_url, cfg.token_url, cfg.userdata_url = build_auth_urls(canvas_url)

   # Scopes that this token will need
   cfg.scope = build_auth_urls.scopes + get_course_groups.scopes

   # Store/retrieve group information from "groups"
   cfg.auth_state_groups_key = "groups"

   # Define auth-state hook
   async def auth_state_hook(authenticator, auth_state):
     if auth_state is None:
       return None

     # Populate JupyterHub groups with names from Canvas course and sections
     auth_state[authenticator.auth_state_groups_key] = await get_course_groups(canvas_url, auth_state["access_token"])

     return auth_state

   cfg.modify_auth_state_hook = modify_auth_state_hook

   # Allow users belonging to the "JupyterHub Users" course to log in
   cfg.allowed_groups = ["course::JupyterHub&20Users"]

   # Set teachers on this course as JupyterHub admins
   cfg.admin_groups = ["course::2i2c&20JupyterHub&20Integration&20Testing::enrollment_type::teacher"]

.. [#scopes] :py:attr:`allowed_scopes <oauthenticator.generic.GenericOAuthenticator.allowed_scopes>` is used in combination with :py:attr:`scope <oauthenticator.generic.GenericOAuthenticator.scope>` to grant access to authenticated users for which the OAuth2 provider granted particular scopes.
