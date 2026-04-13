Canvas
======

.. automodule:: jupyterhub_oauthenticator_authz_helpers.canvas

   :members:


   .. code-block:: python

      from jupyterhub_oauthenticator_authz_helpers.canvas import get_user_groups, get_course_groups, build_auth_urls

      canvas_url = "<CANVAS-URL>"

      async def auth_state_hook(authenticator, auth_state):
        if auth_state:
          access_token = auth_state["access_token"]

          auth_state[authenticator.auth_state_groups_key] = [
            # Populate groups from Canvas courses, using the scheme defined in get_course_groups
            *await get_course_groups(canvas_url, access_token, "course_code"),
            # Populate groups from Canvas groups, using the scheme defined in get_user_groups
            *await get_user_groups(canvas_url, access_token),
          ]

        return auth_state

      cfg = c.GenericOAuthenticator
      cfg.modify_auth_state_hook = auth_state_hook

      cfg.authorize_url, cfg.token_url, cfg.userdata_url = build_auth_urls(canvas_url)

      # Scopes that this token will need, pulled from functions that we've used above
      cfg.scope = [*build_auth_urls.scopes, *get_user_groups.scopes, *get_course_groups.scopes]

.. autofunction:: jupyterhub_oauthenticator_authz_helpers.canvas.get_user_groups

.. autofunction:: jupyterhub_oauthenticator_authz_helpers.canvas.get_course_groups

.. autofunction:: jupyterhub_oauthenticator_authz_helpers.canvas.build_auth_urls
