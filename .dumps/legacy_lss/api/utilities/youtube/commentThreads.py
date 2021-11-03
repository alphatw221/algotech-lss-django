# -*- coding: utf-8 -*-

# Sample Python code for youtube.commentThreads.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os
from creds import load_credentials

import googleapiclient.discovery


def main():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    DEVELOPER_KEY = "AIzaSyBOzpOFg_0iEr5IZIBh7rpX0gVBXce9L7E"
    youtube = googleapiclient.discovery.build(
        "youtube", "v3",
        developerKey=DEVELOPER_KEY,)

    # creds = load_credentials()
    # youtube = googleapiclient.discovery.build(
    #     "youtube", "v3",
    #     credentials=creds
    # )

    def get_comment_threads(videoId):
        request = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=videoId
        )

        while True:
            response = request.execute()

            items = response.get('items', [])
            for item in items:
                comment_object = {
                    'id': item['snippet']['topLevelComment']['id'],
                    'authorChannelId': item['snippet']['topLevelComment']['snippet']['authorChannelId']['value'],
                    'authorDisplayName': item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                    'authorProfileImageUrl': item['snippet']['topLevelComment']['snippet']['authorProfileImageUrl'],
                    'textOriginal': item['snippet']['topLevelComment']['snippet']['textOriginal'],
                    'publishedAt': item['snippet']['topLevelComment']['snippet']['publishedAt'],
                }
                print(comment_object)

            if "nextPageToken" in response:
                request = youtube.commentThreads().list(
                    part="snippet,replies",
                    videoId=videoId,
                    pageToken=response["nextPageToken"]
                )
            else:
                break

    get_comment_threads("63CM0hL-71M")
    # get_comment_threads("wYZXn5Udy2A")


if __name__ == "__main__":
    main()
