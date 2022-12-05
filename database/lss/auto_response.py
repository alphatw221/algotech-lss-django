from ._config import db
from ._config import Collection
from api import models
__collection = db.api_auto_response


class AutoResponse(Collection):

    _collection = db.api_auto_response
    collection_name='api_auto_response'

