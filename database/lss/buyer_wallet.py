from ._config import db
from ._config import Collection
from api import models

__collection = db.api_user_wallet


class BuyerWallet(Collection):

    _collection = db.api_user_wallet
    collection_name='api_user_wallet'
    template = models.user.buyer_wallet.api_user_wallet_template
    
    

