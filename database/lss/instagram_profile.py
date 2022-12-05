from ._config import db
from ._config import Collection

__collection = db.api_instagram_profile


class InstagramProfile(Collection):

    _collection = db.api_instagram_profile
    collection_name='api_instagram_profile'
    
    