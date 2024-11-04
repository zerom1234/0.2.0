from base64 import b64encode
from requests import Response
from mvola_api.api import ClientAPI
from mvola_api.models import AUthResult


class Authentication(ClientAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_token(self, consumer_key: str, consumer_secret: str) -> AUthResult:
        post_data = {
            "grant_type": "client_credentials",
            "scope": "EXT_INT_MVOLA_SCOPE",
        }
        authorization_key = b64encode(f"{consumer_key}:{consumer_secret}".encode('ascii')).decode('utf-8')
        response: Response = self.post('/token', data=post_data, headers={
            'Authorization': f"Basic {authorization_key}",
            'ContentType': 'application/x-www-form-urlencoded',
            'CacheControl': 'no-cache'
        })
        return AUthResult.parse_obj(response.json())
