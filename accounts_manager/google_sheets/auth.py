# apps/accounts_manager/accounts_manager/google_sheets/auth.py
from __future__ import print_function
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from frappe.utils import get_site_path

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_google_service():
    creds = None
    token_path = get_site_path("accounts_manager", "accounts_manager", "google_sheets", "token.json")
    creds_path = get_site_path("accounts_manager", "accounts_manager", "google_sheets", "credentials.json")

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
        creds = flow.run_local_server(port=0)  # Use run_console() on headless server
        with open(token_path, "w") as token_file:
            token_file.write(creds.to_json())

    service = build("sheets", "v4", credentials=creds)
    return service
