from creds import load_credentials, load_credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery
import googleapiclient.errors
import os

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Use the client_secret.json file to identify the application requesting
# authorization. The client ID (from that file) and access scopes are required.
flow = InstalledAppFlow.from_client_config({
    "web": {
        "project_id": "primeval-nectar-322805",
        "client_id": "936983829411-6lq90ld3vs8f4ksbl4gv7hrjlsgkkqjg.apps.googleusercontent.com",
        "client_secret": "k7xYNAy5P7yc5YtZ-ecQ3Qhc",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    }
},
    scopes=['https://www.googleapis.com/auth/youtube.force-ssl',
            "https://www.googleapis.com/auth/youtube.readonly"])


""" Usint redirect_uri to get credentials """
# flow.redirect_uri = 'http://localhost:8000'
# authorization_url, state = flow.authorization_url(
#     access_type='offline',
#     include_granted_scopes='true')

# print(authorization_url)
# print(state)

""" Using local server to get credentials """
# flow.run_local_server()
# credentials = flow.credentials
# print(credentials.to_json())
# print(credentials._refresh_token)

""" Use existing credentials """
creds = load_credentials()


""" Test codes """
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
