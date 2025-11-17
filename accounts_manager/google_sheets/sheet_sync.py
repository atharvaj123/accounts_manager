import frappe
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import date
import logging

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def to_serializable(val):
    if isinstance(val, date):
        return val.isoformat()
    return val

@frappe.whitelist()
def push_expense_to_sheet(expense_name, spreadsheet_id=None, sheet_name=None):
    # Provide defaults if not given
    spreadsheet_id = spreadsheet_id or "1ybHL9ja9W20B9Nl1MFLgd9WEA132RqgKsNWiUWv1Yqs"
    sheet_name = sheet_name or "Sheet1"

    try:
        doc = frappe.get_doc("Expense Entry", expense_name)
        logger.info(f"Fetched Expense Entry: {doc.name}")
    except Exception as e:
        frappe.log_error(message=str(e), title="Failed to fetch Expense Entry doc")
        return {"status": "error", "message": f"Expense Entry not found: {expense_name}"}

    try:
        SERVICE_ACCOUNT_FILE = frappe.get_site_path("private", "files", "google_credential.json")
        credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()

        # Use safe attribute access for expense_category
        expense_category = getattr(doc, "expense_category", "")

        values = [[
            doc.name or "",
            expense_category,
            doc.expense_type or "",
            to_serializable(doc.posting_date),
            doc.amount or 0,
            doc.description or ""
        ]]

        logger.info(f"Pushing values: {values}")

        result = sheet.values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A:F",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={'values': values}
        ).execute()

        updated_rows = result.get("updates", {}).get("updatedRows", 0)
        logger.info(f"Rows updated in Google Sheet: {updated_rows}")

        return {"status": "success", "updated_rows": updated_rows}

    except Exception as e:
        frappe.log_error(message=str(e), title="Failed to push Expense Entry to Google Sheet")
        logger.error(f"Error pushing Expense Entry to Google Sheet: {e}")
        return {"status": "error", "message": str(e)}
