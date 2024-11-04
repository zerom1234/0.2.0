from typing import Optional, List

from pydantic import BaseModel
from datetime import datetime


class Fee(BaseModel):
    feeAmount: float


class AUthResult(BaseModel):
    access_token: str
    scope: str
    token_type: str
    expires_in: int


class Config(BaseModel):
    version: str
    version: str
    xCorrelationID: str
    userLanguage: Optional[str]
    userAccountIdentifier: str
    partnerName: Optional[str]
    xCallbackURL: Optional[str]


class HashedMap(BaseModel):
    key: str
    value: str


class MvolaTransactionState(BaseModel):
    status: str
    serverCorrelationId: str
    notificationMethod: str
    objectReference: str


class MvolaTransactionData(BaseModel):
    amount: float
    currency: str
    descriptionText: str
    requestDate: str
    debitParty: List[HashedMap]
    creditParty: List[HashedMap]
    metadata: List[HashedMap]
    requestingOrganisationTransactionReference: str
    originalTransactionReference: str


class MvolaTransactionResult(BaseModel):
    status: Optional[str]
    serverCorrelationId: Optional[str]
    notificationMethod: Optional[str]
    errorCategory: Optional[str]
    errorCode: Optional[str]
    errorDescription: Optional[str]
    errorDateTime: Optional[datetime]
    errorParameters: Optional[List[HashedMap]]


class MvolaTransactionDetails(BaseModel):
    amount: float
    currency: str
    transactionReference: str
    transactionStatus: str
    createDate: str
    debitParty: List[HashedMap]
    creditParty: List[HashedMap]
    metadata: List[HashedMap]
    fee: Fee
