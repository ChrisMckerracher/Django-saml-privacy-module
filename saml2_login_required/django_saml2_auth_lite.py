"""
    Code is based heavily(including multiple direct copying of code snippets) copied from https://github.com/fangli/django-saml2-auth/blob/master/django_saml2_auth/views.py
    All credit should be given to the original author
"""

from saml2 import (
    BINDING_HTTP_POST,
    BINDING_HTTP_REDIRECT,
    entity,
)
from saml2.client import Saml2Client
from saml2.config import Config as Saml2Config
from django.contrib.auth.models import (User, Group)
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.template import TemplateDoesNotExist
from django.conf import settings
from django.utils.module_loading import import_string
from django.contrib.auth import login


import tempfile

try:
    import urllib2 as _urllib
except:
    import urllib.request as _urllib
    import urllib.error
    import urllib.parse

def get_current_domain(r):
    """
    From original source, structures website domain name
    """
    return '{scheme}://{host}'.format(
        scheme='https' if r.is_secure() else 'http',
        host=r.get_host(),
    )

def _get_saml_client(domain):
    """
    Code mostly copied from original author, with slight adjustments.
    Creates and formats a saml request.
    """
    acs_url = domain + '/sso/acs/'
    time_slack = 0
    mdata = tempfile.NamedTemporaryFile()
    f = open(mdata.name, 'wb')
    f.write(_urllib.urlopen(
        settings.SAML2_AUTH['METADATA_AUTO_CONF_URL']).read()
    )
    f.close()
    saml_settings = {
        'metadata': {
            'local': [mdata.name],
        },
        'entityid': acs_url,
        'service': {
            'sp': {
                'endpoints': {
                    'assertion_consumer_service': [
                        (acs_url, BINDING_HTTP_REDIRECT),
                        (acs_url, BINDING_HTTP_POST)
                    ],
                },
                'allow_unsolicited': True,
                'authn_requests_signed': False,
                'logout_requests_signed': True,
                'want_assertions_signed': True,
                'want_response_signed': False,
            },
        },
        'accepted_time_diff': time_slack,
    }

    spConfig = Saml2Config()
    spConfig.load(saml_settings)
    spConfig.allow_unknown_attributes = True
    saml_client = Saml2Client(config=spConfig)
    mdata.close()
    return saml_client

def _create_new_user(username, email, firstname, lastname):
    """
    From original source
    """
    user = User.objects.create_user(username, email)
    user.first_name = firstname
    user.last_name = lastname
    user.groups = [
        Group.objects.get(name=x) for x in
        settings.SAML2_AUTH
        .get('NEW_USER_PROFILE', {})
        .get('USER_GROUPS', [])
    ]
    user.is_active = settings.SAML2_AUTH \
        .get('NEW_USER_PROFILE', {}) \
        .get('ACTIVE_STATUS', True)
    user.is_staff = settings.SAML2_AUTH \
        .get('NEW_USER_PROFILE', {}) \
        .get('STAFF_STATUS', True)
    user.is_superuser = settings.SAML2_AUTH \
        .get('NEW_USER_PROFILE', {}) \
        .get('SUPERUSER_STATUS', False)
    user.save()
    return user

@csrf_exempt
def acs(r):
    """
    Mostly copied as is from original source
    Removed most error handling, as the library is intended to be used in a testing environment.
    Changed redirection to be the original url
    """
    saml_client = _get_saml_client(get_current_domain(r))
    resp = r.POST.get('SAMLResponse', None)
    next_url = r.session.get('login_next_url')

    authn_response = saml_client.parse_authn_request_response(
        resp, entity.BINDING_HTTP_POST)
    if authn_response is None:
        return HttpResponse("Error at line 115")

    user_identity = authn_response.get_identity()
    if user_identity is None:
        return HttpResponse("Error at line 118")


    user_email = user_identity[
        settings.SAML2_AUTH
        .get('ATTRIBUTES_MAP', {})
        .get('email', 'Email')
    ][0]
    user_name = user_identity[
        settings.SAML2_AUTH
        .get('ATTRIBUTES_MAP', {})
        .get('username', 'UserName')
    ][0]
    user_first_name = user_identity[
        settings.SAML2_AUTH
        .get('ATTRIBUTES_MAP', {})
        .get('first_name', 'FirstName')
    ][0]
    user_last_name = user_identity[
        settings.SAML2_AUTH
        .get('ATTRIBUTES_MAP', {})
        .get('last_name', 'LastName')
    ][0]

    target_user = None
    is_new_user = False

    try:
        target_user = User.objects.get(username=user_name)
        if settings.SAML2_AUTH.get('TRIGGER', {}).get('BEFORE_LOGIN', None):
            import_string(
                settings.SAML2_AUTH['TRIGGER']['BEFORE_LOGIN']
            )(user_identity)
    except User.DoesNotExist:
        target_user = _create_new_user(
            user_name, user_email,
            user_first_name, user_last_name
        )
        if settings.SAML2_AUTH.get('TRIGGER', {}).get('CREATE_USER', None):
            import_string(
                settings.SAML2_AUTH['TRIGGER']['CREATE_USER']
            )(user_identity)
        is_new_user = True

    r.session.flush()

    if target_user.is_active:
        target_user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(r, target_user)
    else:
        return HttpResponse("Error at line 169")

    if is_new_user:
        try:
            return render(
                r, 'django_saml2_auth/welcome.html',
                {'user': r.user}
            )
        except TemplateDoesNotExist:
            return HttpResponseRedirect(next_url)
    else:
        return HttpResponseRedirect(next_url)

def signin(r):
    """
    Copied mostly as-is from source.
    Changes such that redirect url is always the original url
    """
    try:
        import urlparse as _urlparse
        from urllib import unquote
    except:
        import urllib.parse as _urlparse
        from urllib.parse import unquote
    next_url = r.get_full_path()
    r.session['login_next_url'] = next_url

    saml_client = _get_saml_client(get_current_domain(r))
    _, info = saml_client.prepare_for_authenticate()

    redirect_url = None

    for key, value in info['headers']:
        if key == 'Location':
            redirect_url = value
            break
    return HttpResponseRedirect(redirect_url)