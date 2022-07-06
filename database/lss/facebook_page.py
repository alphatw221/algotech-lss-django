from ._config import db
from ._config import Collection

__collection = db.api_facebook_page


class FacebookPage(Collection):

    _collection = db.api_facebook_page
    collection_name='api_facebook_page'
    
   