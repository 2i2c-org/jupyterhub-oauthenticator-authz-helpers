:html_theme.sidebar_secondary.remove: true

.. jupyterhub_oauthenticator_authz_helpers documentation master file, created by
   sphinx-quickstart on Mon Apr 13 13:12:17 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

JupyterHub Authentication and Authorization Helpers
===================================================

The :py:class:`GenericOAuthenticator <oauthenticator.generic.GenericOAuthenticator>` JupyterHub authenticator is highly versatile for integrating JupyterHub with third-part OAuth providers. Rather than building custom :py:class:`OAuthenticator <oauthenticator.oauth2.OAuthenticator>` subclasses, the helpers provided by this library may be used to support new OAuth providers.

.. toctree::
   :maxdepth: 1
   :caption: How-to Guide

   how-to/index

.. toctree::
   :maxdepth: 1
   :caption: API Reference

   api/index
