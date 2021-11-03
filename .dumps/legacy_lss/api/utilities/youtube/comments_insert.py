# -*- coding: utf-8 -*-

# Sample Python code for youtube.comments.insert
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os

import googleapiclient.discovery
import googleapiclient.errors
from creds import load_credentials

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]


def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    creds = load_credentials()

    youtube = googleapiclient.discovery.build(
        "youtube", "v3",
        credentials=creds
    )

    request = youtube.comments().insert(
        part="snippet",
        body={
            "snippet": {
                "textOriginal": "REPLY",
                "parentId": "UgwDeN3WhbgCFtZO2j94AaABAg"
            }
        }
    )
    response = request.execute()

    print(response)


if __name__ == "__main__":
    main()
