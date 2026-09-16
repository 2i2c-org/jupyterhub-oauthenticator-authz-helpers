Set Up Canvas Authentication
============================

.. epigraph::

   Authentication [...] is the act of proving an assertion, such as the identity of a computer system user.

   -- `Wikipedia <https://en.wikipedia.org/wiki/Authentication>`__

Canvas is a `Learning Management System <https://en.wikipedia.org/wiki/Learning_management_system>`__ built by Instructure Holdings that is widely used across educational instutions to provide students with online learning. With the :py:mod:`jupyterhub_oauthenticator_authz_helpers.canvas`, it is possible to use Canvas as an *authentication provider* which allows users with access to a particular Canvas instance to log-in to a JupyterHub.

Installing the Library
----------------------

To use these helpers, you must first install the ``jupyterhub-oauthenticator_authz_helpers`` package from PyPI into the same environment as your JupyterHub itself. For `Zero to JupyterHub <https://zero-to-jupyterhub.readthedocs.io/>`__ users, this means creating a custom Docker image that installs this package alongside the JupyterHub dependencies.


Authorizing with the Canvas API
-------------------------------

JupyterHubs's *OAuthenticator* library ships with a :py:class:`GenericOAuthenticator <oauthenticator.generic.GenericOAuthenticator>` which interfaces with `OAuth2 <https://en.wikipedia.org/wiki/OAuth>`__ identity providers. In order to complete one OAuth flow, the authenticator requires the :py:attr:`authorize_url <oauthenticator.generic.GenericOAuthenticator.authorize_url>` and :py:attr:`token_url <oauthenticator.generic.GenericOAuthenticator.token_url>` attributes to be configured that points to the OAuth2 authorization and token endpoints of the Canvas instance. We will generate these URLs using the :py:func:`build_auth_urls <jupyterhub_oauthenticator_authz_helpers.canvas.build_auth_urls>` helper.

.. code-block:: python

   from jupyterhub_oauthenticator_authz_helpers import build_auth_urls

   canvas_url = "<CANVAS-URL>"

   cfg = c.GenericOAuthenticator

   # Configure auth and token URLs
   cfg.authorize_url, cfg.token_url, _ = build_auth_urls(canvas_url)

   # Scopes that this token will need
   cfg.scope = build_auth_urls.scopes

Whilst in this case, we could simply write the authorize URL and scopes by hand, using these functions makes it slightly harder to make a typo, or forget a scope.

Authenticating the Canvas User
------------------------------

Together, the :py:attr:`authorize_url <oauthenticator.generic.GenericOAuthenticator.authorize_url>` and :py:attr:`token_url <oauthenticator.generic.GenericOAuthenticator.token_url>` endpoints returns an access token that provides authorization to a Canvas instance's resources on behalf of the current Canvas user. This alone is insufficient to set-up Canvas authentication, as the authenticator does not have the ability to determine *who* is accessing the hub from this token alone.

For this, we'll need to query a user-data URL that returns identity information about the current token holder. Let's now configure the :py:attr:`userdata_url <oauthenticator.generic.GenericOAuthenticator.userdata_url>` to obtain structured information about the Canvas user's identity, and configure the authenticator to derive a username from this data. For example, if the Canvas API returns a ``login_id`` field in the ``userdata_url`` response:

.. code-block:: python
   :emphasize-lines: 8, 14

   from jupyterhub_oauthenticator_authz_helpers import build_auth_urls

   canvas_url = "<CANVAS-URL>"

   cfg = c.GenericOAuthenticator

   # Configure various auth URLs
   cfg.authorize_url, cfg.token_url, cfg.userdata_url = build_auth_urls(canvas_url)

   # Scopes that this token will need
   cfg.scope = build_auth_urls.scopes

   # Indicate which user-data item yields the username
   cfg.username_claim = "login_id"

Now we've successfully configured our JupyterHub with the ability to identify the username of user that log-in with Canvas. However, these users will not, by default, be able to access the hub. For that, we must visit the topic of :doc:`authentication <canvas-authorization>`.
