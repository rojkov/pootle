"""Authentication code."""

from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ImproperlyConfigured


def basic_challenge(realm = None):
    """Create 401 HttpResponse."""
    if realm is None:
        realm = getattr(settings, "BASIC_AUTH_REALM", "mbs")
    response =  HttpResponse("Authorization Required", mimetype="text/plain")
    response["WWW-Authenticate"] = 'Basic realm="%s"' % (realm)
    response.status_code = 401
    return response


def basic_authenticate(authentication):
    """Parse the authentication string and try to authenticate."""
    # Taken from paste.auth

    (authmeth, auth) = authentication.split(' ', 1)
    if 'basic' != authmeth.lower():
        return None
    auth = auth.strip().decode('base64')
    username, password = auth.split(':', 1)
    return authenticate(username = username, password = password)


class BasicAuthenticationMiddleware(object):
    """Basic Authentication Middleware."""

    def process_request(self, request):
        """Process request."""

        if not hasattr(request, "user"):
            raise ImproperlyConfigured(
                "The MBS basic auth middleware requires the"
                " authentication middleware to be installed.  Update your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the BasicAuthenticationMiddleware class.")
        if request.user.is_authenticated():
            return

        if not request.META.get("HTTP_AUTHORIZATION", None):
            logout(request)
            return basic_challenge()
        user = basic_authenticate(request.META["HTTP_AUTHORIZATION"])
        if user is None:
            return basic_challenge()
        else:
            login(request, user)
