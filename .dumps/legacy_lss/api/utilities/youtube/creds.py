from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


def load_credentials():
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

    flow.run_local_server()
    credentials = flow.credentials

    return credentials


def load_credentials(token="yaa29.-bROcJjC220Wyh429rMqVFz9iOsMl-U-1Kiq6APB7DKZqCiZjTLN0KfTxQA",
                     refresh_token="1//0ecIEXahGHQqQCgYIARAAGA4SNwF-L9IrPvNMp1fWvSNxYo8803Gezn1cgCcJ8i0MxUixMhSU986t41l6rjh29ZnngJEUB3qAAu4",
                     token_uri="https://oauth2.googleapis.com/token",
                     client_id="936983829411-6lq90ld3vs8f4ksbl4gv7hrjlsgkkqjg.apps.googleusercontent.com",
                     client_secret="k7xYNAy5P7yc5YtZ-ecQ3Qhc",
                     scopes=["https://www.googleapis.com/auth/youtube.force-ssl",
                             "https://www.googleapis.com/auth/youtube.readonly"],
                     expiry="2021-08-16T08:54:26.723386Z"):
    creds = Credentials.from_authorized_user_info({"token": token,
                                                   "refresh_token": refresh_token,
                                                   "token_uri": token_uri,
                                                   "client_id": client_id,
                                                   "client_secret": client_secret,
                                                   "scopes": scopes,
                                                   "expiry": expiry})
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

    return creds
