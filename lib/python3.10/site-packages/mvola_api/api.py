from requests import Session
from urllib.parse import urljoin


class ClientAPI(Session):
    def __init__(self, prefix_url=None, *args, **kwargs):
        super(ClientAPI, self).__init__()
        self.prefix_url = prefix_url

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.prefix_url, url)
        print('URL : ', url)
        return super(ClientAPI, self).request(method, url, *args, **kwargs)
