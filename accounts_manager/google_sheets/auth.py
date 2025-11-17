from __future__ import print_function
import os
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from frappe.utils import get_site_path

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_google_service():
    creds = None
    token_path = get_site_path("accounts_manager", "accounts_manager", "google_sheets", "token.json")
    creds_path = get_site_path("accounts_manager", "accounts_manager", "google_sheets", "credentials.json")

    try:
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            logging.info("Loaded Google API token from %s", token_path)

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            logging.info("Refreshed Google API access token.")
            with open(token_path, "w") as token_file:
                token_file.write(creds.to_json())

        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            # Detect headless environment; fallback to console auth if needed
            try:
                creds = flow.run_local_server(port=0)
            except Exception as e:
                logging.warning("Interactive auth failed, falling back to console: %s", e)
                creds = flow.run_console()

            with open(token_path, "w") as token_file:
                token_file.write(creds.to_json())
            logging.info("Obtained new Google API token.")

    except Exception as e:
        logging.error("Failed to get Google Sheets credentials: %s", e)
        raise

    service = build("sheets", "v4", credentials=creds)
    return service
