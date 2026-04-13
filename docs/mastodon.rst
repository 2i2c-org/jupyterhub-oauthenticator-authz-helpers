
.. automodule:: jupyterhub_oauthenticator_authz_helpers.mastodon

   :members:

.. autofunction:: jupyterhub_oauthenticator_authz_helpers.mastodon.get_followed_groups

Example
-------

.. code-block:: python

   from jupyterhub_oauthenticator_authz_helpers.mastodon import get_followed_groups, build_auth_urls, build_userdata_url

   mastodon_url = "<MASTODON_URL>"

   id_to_alias = {
        "<ACCOUNT-ID-1>": "group-one",
        "<ACCOUNT-ID-2>": "group-two",
   }

   async def auth_state_hook(authenticator, auth_state):
     if auth_state:
       access_token = auth_state["access_token"]

       auth_state[authenticator.auth_state_groups_key] = [
         # Populate groups from Canvas courses, using the scheme defined in get_course_groups
         *await get_followed_groups(mastodon_url, access_token, id_to_alias),
       ]

     return auth_state

   cfg = c.GenericOAuthenticator
   cfg.modify_auth_state_hook = auth_state_hook

   cfg.token_url, cfg.authorize_url = build_auth_urls(mastodon_url)
   cfg.userdata_url = build_userdata_url(mastodon_url)

   # Scopes that this token will need, pulled from functions that we've used above
   cfg.scope = [*build_userdata_url.scopes, *get_followed_groups.scopes]
