from authlib.integrations.django_client import OAuth

from .helpers import OAuthMod
from .models import CustomUser, OAuth2Token
from django.http import HttpResponse
from django.utils.crypto import get_random_string

STATE_CODE_LENGTH = 20


def update_token(name, token, refresh_token=None, access_token=None):
    if refresh_token:
        item = OAuth2Token.objects.get(name=name, refresh_token=refresh_token)
    elif access_token:
        item = OAuth2Token.objects.get(name=name, access_token=access_token)
    else:
        return
    # update old token
    item.access_token = token['access_token']
    item.refresh_token = token.get('refresh_token')
    item.expires_at = token['expires_at']
    item.save()


# def fetch_token(name, request):
#     token = OAuth2Token.objects.get(
#         name=name,
#         user=request.user
#     )
#     return token.to_token()


# Init the OAuth
# oauth = OAuthMod(fetch_token=fetch_token, update_token=update_token)
# oauth.register(
#     name='bars_web_mchs',
# )


# def login(request):
#     state = get_random_string(STATE_CODE_LENGTH)
#     redirect_uri = request.build_absolute_uri('http://127.0.0.1:8000/web/authorize')
#     request.session['session_state'] = state
#     extra_para = {'state': state}
#
#     return oauth.bars_web_mchs.authorize_redirect(request, redirect_uri, **extra_para)
#
#
# def authorize(request):
#     app_state = request.GET.get('state', '')
#     session_state = request.session.get('session_state', '')
#     token = oauth.bars_web_mchs.authorize_access_token(request)
#     user = oauth.bars_web_mchs.userinfo(token=token['access_token'])
#
#     if app_state == session_state:
#         return HttpResponse("welcome")
#     else:
#         return HttpResponse("state not match")


from datetime import datetime, timedelta


def process_token(request, token, username):
    provider = 'bars_web_mchs'
    email = username

    try:
        # Retrieve the related user
        user = CustomUser.objects.get(email=email, provider=provider)
    except CustomUser.DoesNotExist:
        # Create user if not exists
        user = CustomUser.objects.create_user(username=email, email=email, provider=provider)
        oauth2token = dict()
        oauth2token['name'] = 'bars_web_mchs'
        oauth2token['token_type'] = token['token_type']
        oauth2token['access_token'] = token['access_token']
        if 'refresh_token' in token.keys():
            oauth2token['refresh_token'] = token['refresh_token']

        if 'expires_at' in token.keys():
            oauth2token['expires_at'] = token['expires_at']
        current_time = datetime.now()
        if 'expires_in' in token.keys():
            expiry_datetime = current_time + timedelta(seconds=token['expires_in'])
        else:
            expiry_datetime = current_time + timedelta(days=10)
        oauth2token['expires_in'] = expiry_datetime
        OAuth2Token.objects.update_or_create(user=user,
                                             defaults=oauth2token)
