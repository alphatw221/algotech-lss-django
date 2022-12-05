from ._config import db
from ._config import Collection

__collection = db.api_youtube_channel


class YoutubeChannel(Collection):

    _collection = db.api_youtube_channel
    collection_name='api_youtube_channel'
    
   