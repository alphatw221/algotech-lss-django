from ._config import db
from ._config import Collection

__collection = db.api_campaign


class Campaign(Collection):

    _collection = db.api_campaign