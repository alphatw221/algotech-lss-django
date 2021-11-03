# -*- coding: utf-8 -*-

# Sample Python code for youtube.channels.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os

from creds import load_credentials
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    creds = load_credentials()

    youtube = googleapiclient.discovery.build(
        "youtube", "v3",
        credentials=creds
    )

    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        mine=True
    )
    response = request.execute()

    print(response)


if __name__ == "__main__":
    main()
