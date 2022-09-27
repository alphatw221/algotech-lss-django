from ._config import db
from ._config import Collection
from api import models

__collection = db.api_user


class User(Collection):

    _collection = db.api_user
    collection_name='api_user'
    template = models.user.user.api_user_template
    

