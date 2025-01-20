.. role:: console(code)
   :language: console
.. role:: python(code)
   :language: python

.. _user_authorization:

User Authorization (OIDC)
=========================
Access to data and process units can be restricted by a user authorization integration with Azure which employs an oAuth/OIDC login flow.
It is also possible for a headless application to access restricted resources using a client secret configured in Azure.

.. contents:: Table of Contents
  :local:
  :depth: 3

Azure Configuration
-------------------
The integration works for single tenant `App Registrations`.
Configure the App Registration and the associated Enterprise Application.

App Registration
^^^^^^^^^^^^^^^^
Configure the `App Registration` as follows:

* Add a Single-page application platform with callback URL :console:`http://localhost:9800/auth-callback` where `9800` is the local development aggregator port. In a production environment the callback URL might be :console:`https://openpectus.com/auth-callback`.
* Issue Access tokens *and* ID tokens
* Configure the App Registration to be accessible in this organization only
* (Optional) Create a client secret for a headless application
* (Optional) Add optional claim for :console:`idtyp` for access tokens if you use headless applications. This claim enables the integration to correctly identify that it is being accessed from an authorized headless application.
* Grant API permissions for:

    * :console:`offline_access`
    * :console:`openid`
    * :console:`profile`
    * :console:`User.Read`
    
* (Optional) Define app roles. When a user is authenticated then the role assignments for that user are used to restrict access.

Take note of the `Application (client) ID` and the `Directory (tenant) ID`. These will be used to configure authentication in Open Pectus.

Enterprise Application
^^^^^^^^^^^^^^^^^^^^^^
Configure the accompanying `Enterprise App` as follows:

* Enable for users to sign-in
* (Optional) Do *not* require assignment of users
* (Optional) Assign roles defined in the App Registration to specific users or groups.

Open Pectus Configuration
-------------------------

Aggregator
^^^^^^^^^^
Configuration is managed by setting environment variables to enable different setups for local development, test/staging servers, and production environments. These environment variables only apply to the aggregator.

Set the following environment variables:

* :console:`ENABLE_AZURE_AUTHENTICATION`: :console:`true` or :console:`false` to enable/disable Azure AD integration.
* :console:`AZURE_DIRECTORY_TENANT_ID`: The `Directory (tenant) ID` GUID for your Azure AD tenant/directory.
* :console:`AZURE_APPLICATION_CLIENT_ID`: The `Application (client) ID` for the App Registration in Azure.

Engines
^^^^^^^
Access to individual engines can be restricted via roles. Roles are defined in the Azure `App Registration` and assigned to users in the Azure `Enterprise App`. Access can then be restricted to those users who have any of the roles in a given list. This is configured in the :ref:`unit_operation_definition` using the :python:`with_required_roles(["Role",])` method.

Users who are assigned to *any* role in the list of required roles has access to all aspects of the UOD.

Headless applications all have the role :console:`Daemon`. To give access to a headless application the role :console:`Daemon` must be in the list of required roles.

Access Open Pectus via Headless Application
-------------------------------------------
It is possible to authenticate with a `client secret`. Applications that authenticate this way are assigned user name :console:`Daemon` and role :console:`Daemon`.
The API is documented in :ref:`openapi_specification`. An example written in Python is stated in :numref:`headless_example`.

.. _headless_example:
.. code-block:: python
   :caption: Example Python code to acquire token and access restricted API.
             :console:`pip install msal PyJWT requests`

   import msal
   import jwt
   import requests


   def acquire_access_token(client_id: str,
                            tenant_id: str,
                            client_secret: str) -> str:
       """
       Acquire Access Token using Daemon Client Secret flow.
       """
       # Configure URLs.
       authority = f"https://login.microsoftonline.com/{tenant_id}"
       issuer_url = f"https://sts.windows.net/{tenant_id}/"
       jwks_url = f"{authority}/discovery/v2.0/keys"
       # Configure scope
       scopes = [f"{client_id}/.default",]

        msal_result = msal.ConfidentialClientApplication(
           client_id,
           authority=authority,
           client_credential=client_secret
       ).acquire_token_for_client(scopes=scopes)

       access_token = msal_result.get("access_token", None)  # type: ignore
       if access_token is None:
           raise Exception("Authentication was not successful.")

       # Verify that key is any good
       access_token_dict: dict[str, str | list[str]] = jwt.decode(
           access_token,
           jwt.PyJWKClient(jwks_url).get_signing_key_from_jwt(access_token),
           algorithms=["RS256"],
           audience=client_id,
           issuer=issuer_url,
       )
       return access_token


   access_token = acquire_access_token(
       client_id="...",
       tenant_id="...",
       client_secret="...",
   )

   recent_runs = requests.get(
       "https://openpectus.com/api/recent_runs/",
       headers={"X-Identity": access_token,},
   )
   print(recent_runs, recent_runs.json())

