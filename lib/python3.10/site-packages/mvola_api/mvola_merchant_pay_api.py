from mvola_api.auth import Authentication
from mvola_api.data import SANDBOX_URL
from mvola_api.models import AUthResult
from mvola_api.transaction import Transaction


class MVolaMerchantPayAPI(Transaction):

    def __init__(self, url: str = SANDBOX_URL, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix_url = url

    def set_access_token(self, access_token: str):
        self.headers.update({"Authorization": f'Bearer {access_token}'})

    def revoke_token(self, consumer_key: str, consumer_secret: str, update_token: bool = True) -> AUthResult:
        auth: Authentication = Authentication(prefix_url=self.prefix_url)
        response: AUthResult = auth.get_token(consumer_key, consumer_secret)
        if update_token:
            self.set_access_token(response.access_token)
        return response
