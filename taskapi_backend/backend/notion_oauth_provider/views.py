from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import NotionProvider


class NotionAdapter(OAuth2Adapter):
    provider_id = NotionProvider.id
    settings = app_settings.PROVIDERS.get(provider_id, {})
    access_token_url = "https://api.notion.com/v1/oauth/token"
    authorize_url = "https://api.notion.com/v1/oauth/authorize"
    basic_auth = True

    def complete_login(self, request, app, token, response):
        assert response["owner"]["type"] == "user"
        return self.get_provider().sociallogin_from_response(request, response)

    def is_open_for_signup(self, request):
        return True


oauth2_login = OAuth2LoginView.adapter_view(NotionAdapter)
oauth2_callback = OAuth2CallbackView.adapter_view(NotionAdapter)
