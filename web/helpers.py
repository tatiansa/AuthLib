import requests
from authlib.integrations.base_client import OAuth2Mixin, OpenIDMixin, BaseApp, OAuthError, BaseOAuth
from authlib.integrations.django_client import DjangoIntegration
from authlib.integrations.django_client.apps import DjangoAppMixin, DjangoOAuth1App
from authlib.integrations.requests_client import OAuth2Session


class OAuth2SessionMod(OAuth2Session):
    pass


class DjangoOAuth2AppMod(DjangoAppMixin, OAuth2Mixin, OpenIDMixin, BaseApp):
    client_cls = OAuth2SessionMod

    def authorize_access_token(self, request, **kwargs):

        if request.method == 'GET':
            error = request.GET.get('error')
            if error:
                description = request.GET.get('error_description')
                raise OAuthError(error=error, description=description)
            params = {
                'code': request.GET.get('code'),
                'state': request.GET.get('state'),
            }
        else:
            params = {
                'code': request.POST.get('code'),
                'state': request.POST.get('state'),
            }

        state_data = self.framework.get_state_data(request.session, params.get('state'))
        self.framework.clear_state_data(request.session, params.get('state'))
        params = self._format_state_params(state_data, params)
        token = self.fetch_access_token(**params, **kwargs)

        # костыль для работы внутренних механизмов расшифровки id_token
        # вообще информация о пользователе зашифрована в этом блоку токена, но
        # мы почему то не передаём параметр kid и вынуждены посылать отдельный запрос
        if 'id_token' in token and 'nonce' in state_data:
            metadata = self.load_server_metadata()
            with self._get_oauth_client(**metadata) as client:
                response = requests.session().post(
                    metadata['userinfo_endpoint'],
                    data={
                        'access_token': token['access_token'],
                    }
                )

                token['userinfo'] = response.json()

        return token


class OAuthMod(BaseOAuth):
    oauth1_client_cls = DjangoOAuth1App
    oauth2_client_cls = DjangoOAuth2AppMod
    framework_integration_cls = DjangoIntegration