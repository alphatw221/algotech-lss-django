from ._config import db
from ._config import Collection

__collection = db.api_twitch_channel


class TwitchChannel(Collection):

    _collection = db.api_twitch_channel
    collection_name='api_twitch_channel'
    
    