from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.account.models import EmailAddress


class NotionAccount(ProviderAccount):
    def get_user(self):
        return self.account.extra_data["owner"]["user"]

    def get_name(self):
        return self.get_user().get("name")

    def get_workspace_name(self):
        return self.account.extra_data["workspace_name"]

    def to_str(self):
        name = self.get_name()
        workspace = self.get_workspace_name()
        return f"{name} ({workspace})"


class NotionProvider(OAuth2Provider):
    id = "taskapi_notion"
    name = "Notion"
    account_class = NotionAccount

    def get_default_scope(self):
        scope = []
        return scope

    def extract_uid(self, data):
        user_id = data["owner"]["user"]["id"]
        workspace_id = data["workspace_id"]
        return f"{user_id}_{workspace_id}"

    def extract_common_fields(self, data):
        return dict(
            username=f"n_{self.extract_uid(data)}",
            last_name=data.get("owner").get("user").get("name"),
        )

    def extract_email_addresses(self, data):
        email = data.get("owner").get("user").get("person").get("email")

        return [EmailAddress(email=email, verified=True, primary=True)]


provider_classes = [NotionProvider]
