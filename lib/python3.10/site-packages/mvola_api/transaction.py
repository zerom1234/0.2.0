from mvola_api.api import ClientAPI
from mvola_api.data import MVOLA_MERCHANT_API_URL
from mvola_api.models import MvolaTransactionDetails, MvolaTransactionState, MvolaTransactionData, MvolaTransactionResult, Config
from requests import Response


class Transaction(ClientAPI):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_details(self, transactionId: str) -> MvolaTransactionDetails:
        response: Response = self.get(f'{MVOLA_MERCHANT_API_URL}/{transactionId}')
        return MvolaTransactionDetails.parse_obj(response.json())

    def get_status(self, serverCorrelationId: str) -> MvolaTransactionState:
        response: Response = self.get(f'{MVOLA_MERCHANT_API_URL}/status/{serverCorrelationId}')
        return MvolaTransactionState.parse_obj(response.json())

    def initiate_transaction(self, params: MvolaTransactionData) -> MvolaTransactionResult:
        params.amount = str(params.amount)
        response: Response = self.post(f'{MVOLA_MERCHANT_API_URL}', data=params.dict())
        print(response.json())
        return MvolaTransactionResult.parse_obj(response.json())

    def init_config(self, config: Config):
        self.headers.update({
            "Version": config.version,
            "X-CorrelationID": config.xCorrelationID,
            "Cache-Control": "no-cache",
            "UserAccountIdentifier": config.userAccountIdentifier
        })
        if config.partnerName is not None:
            self.headers.update({
                "PartnerName": config.partnerName
            })
        if config.xCallbackURL is not None:
            self.headers.update({
                "X-Callback-URL": config.xCallbackURL
            })
        if config.userLanguage is not None:
            self.headers.update({
                "UserLanguage": config.userLanguage
            })
