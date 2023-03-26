from authlib.integrations.base_client import OAuthError
from authlib.oauth2.rfc6749 import OAuth2Token
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from AuthLib import settings
from web import views
from web.helpers import OAuthMod


class OAuthMiddleware(MiddlewareMixin):

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.oauth = OAuthMod()

    def process_request(self, request):
        def update_token(token, refresh_token, access_token):
            request.session['token'] = token
            return None

        sso_client = self.oauth.register(
            settings.OAUTH_CLIENT_NAME,
            overwrite=True,
            **settings.OAUTH_CLIENT,
            update_token=update_token
        )

        if request.path.startswith('/web/authorize'):
            self.clear_session(request)
            request.session['token'] = sso_client.authorize_access_token(request)
            if self.get_current_user(sso_client, request) is not None:
                redirect_uri = request.session.pop('redirect_uri', None)
                if redirect_uri is not None:
                    return redirect(redirect_uri)

                return redirect(views.index)

        if request.session.get('token', None) is not None:
            current_user = self.get_current_user(sso_client, request)
            if current_user is not None:
                return self.get_response(request)

        # remember redirect URI for redirecting to the original URL.
        request.session['redirect_uri'] = request.path
        return sso_client.authorize_redirect(request, settings.OAUTH_CLIENT['redirect_uri'])

    # fetch current login user info
    # 1. check if it's in cache
    # 2. fetch from remote API when it's not in cache
    @staticmethod
    def get_current_user(sso_client, request):
        token = request.session.get('token', None)
        if token is None or 'access_token' not in token:
            return None

        if not OAuth2Token.from_dict(token).is_expired() and 'user' in request.session:
            return request.session['user']

        try:
            res = sso_client.get(settings.OAUTH_CLIENT['userinfo_endpoint'], token=OAuth2Token(token))
            if res.ok:
                request.session['user'] = res.json()
                return res.json()
        except OAuthError as e:
            print(e)
        return None

    @staticmethod
    def clear_session(request):
        try:
            del request.session['user']
            del request.session['token']
        except KeyError:
            pass

    def __del__(self):
        print('destroyed')