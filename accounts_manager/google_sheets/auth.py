from __future__ import print_function
import os
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from frappe.utils import get_site_path

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
logger = logging.getLogger(__name__)

def get_google_service():
    creds = None
    token_path = get_site_path("accounts_manager", "accounts_manager", "google_sheets", "token.json")
    creds_path = get_site_path("accounts_manager", "accounts_manager", "google_sheets", "credentials.json")

    try:
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            logger.info("Loaded token from %s", token_path)

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            logger.info("Refreshed access token.")
            with open(token_path, "w") as token_file:
                token_file.write(creds.to_json())

        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            try:
                creds = flow.run_local_server(port=0)
            except Exception as e:
                logger.warning(f"Interactive auth failed: {e}, fallback to console flow.")
                creds = flow.run_console()

            with open(token_path, "w") as token_file:
                token_file.write(creds.to_json())
            logger.info("Obtained new credentials and saved token.")
    except Exception as e:
        logger.error(f"Failed to authenticate Google API: {e}")
        raise

    service = build("sheets", "v4", credentials=creds)
    return service
