=====================================
Django SAML2 Login Required
=====================================

:Author: Fang Li, Christopher Mckerracher
:Version: 0.1

This project aims to provide functionality similar to Django's login_required decorator, with
the added bonus of integrating with saml2. Users will be redirected to their SAML2 Identity 
Provider's login page provided that they are not logged in.

A major benefit of this project is that it allows developers to share web applications/web
pages, etc with only selected, approved individuals over the internet.

This project is currently using a stripped down version of Fang Li's django_saml2_auth 
library, as this project should only be used on applications still in 'dev mode'.

See the original project [here](https://github.com/fangli/django-saml2-auth>)

A demo of a web page using the project's decorator can be viewed [here](https://okta-login-required.herokuapp.com/decorator/with/)
Compared to the same web page without the project's decorator [here](https://okta-login-required.herokuapp.com/decorator/without)


Dependencies
============

This plugin is compatible with Django 1.10 The `pysaml2` Python
module is required.



Install
=======

You can install this plugin via:

.. code-block:: bash

    # git clone https://github.com/ChrisMckerracher/saml2_login_required
    # cd django-saml2-auth
    # python setup.py install

xmlsec is also required by pysaml2:

.. code-block:: bash

    # yum install xmlsec1
    // or
    # apt-get install xmlsec1


How to use?
===========

#. In your root project's urls.py, add this line to your urlpatterns:

    .. code-block:: python

        from saml2_login_required.django_saml2_auth_lite import acs

        # This is your SP's destination endpoint. Your SAML configuration
        #should match this 
        url(r'^sso/acs/$', acs),

#. Add 'saml2_login_required' to INSTALLED_APPS

    .. code-block:: python

        INSTALLED_APPS = [
            '...',
            'saml2_login_required',
        ]

#. In settings.py, add the SAML2 related configuration.

    Please note, the only required setting is **METADATA_AUTO_CONF_URL**.
    The following block shows all required and optional configuration settings
    and their default values.

    .. code-block:: python

        SAML2_AUTH = {
            # Required setting
            'METADATA_AUTO_CONF_URL': '[The auto(dynamic) metadata configuration URL of SAML2]',

            # Optional settings
            'NEW_USER_PROFILE': {
                'USER_GROUPS': [],  # The default group name when a new user logs in
                'ACTIVE_STATUS': True,  # The default active status for new users
                'STAFF_STATUS': False,  # The staff status for new users
                'SUPERUSER_STATUS': False,  # The superuser status for new users
            },
            'ATTRIBUTES_MAP': {  # Change Email/UserName/FirstName/LastName to corresponding SAML2 userprofile attributes.
                'email': 'Email',
                'username': 'UserName',
                'first_name': 'FirstName',
                'last_name': 'LastName',
            },
        }

#. In your SAML2 SSO identity provider, set the Single-sign-on URL and Audience
   URI(SP Entity ID) to http://your-domain/sso/acs/

#. To make a view required sign on, with SSO identity provider redirection, add
   this line to your views.py:

   .. code-block:: python
        
        from saml2_login_required.decorators import saml2_login_required

#. From here, just add the decorator to your view.

   .. code-block:: python
        
        @saml2_login_required
        def view_example(r):

Explanation
-----------

**METADATA_AUTO_CONF_URL** Auto SAML2 metadata configuration URL

**NEW_USER_PROFILE** Default settings for newly created users

**ATTRIBUTES_MAP** Mapping of Django user attributes to SAML2 user attributes

For Okta Users
==============

I created this plugin originally for Okta.

The METADATA_AUTO_CONF_URL needed in `settings.py` can be found in the Okta
web UI by navigating to the SAML2 app's `Sign On` tab, in the Settings box.
You should see :

`Identity Provider metadata is available if this application supports dynamic configuration.`

The `Identity Provider metadata` link is the METADATA_AUTO_CONF_URL.


How to Contribute
=================

#. Check for open issues or open a fresh issue to start a discussion around a feature idea or a bug.
#. Fork `the repository`_ on GitHub to start making your changes to the **master** branch (or branch off of it).
#. Write a test which shows that the bug was fixed or that the feature works as expected.
#. Send a pull request and bug the maintainer until it gets merged and published. :) Make sure to add yourself to AUTHORS_.

.. _`the repository`: http://github.com/fangli/django-saml2-auth
.. _AUTHORS: https://github.com/fangli/django-saml2-auth/blob/master/AUTHORS.rst
