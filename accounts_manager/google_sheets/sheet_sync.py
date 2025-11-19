import frappe
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import date, datetime
import os
import logging

logger = logging.getLogger(__name__)
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def to_serializable(val):
    if val is None:
        return ""
    if isinstance(val, (date, datetime)):
        return val.isoformat()
    return str(val)

@frappe.whitelist()
def push_expense_to_sheet(expense_name, spreadsheet_id=None, sheet_name=None):
    spreadsheet_id = spreadsheet_id or "1ybHL9ja9W20B9Nl1MFLgd9WEA132RqgKsNWiUWv1Yqs"
    sheet_name = sheet_name or "Sheet1"

    # 1️⃣ Fetch the Expense Entry doc
    try:
        doc = frappe.get_doc("Expense Entry", expense_name)
    except Exception as e:
        frappe.log_error(message=str(e), title="Failed to fetch Expense Entry doc")
        return {"status": "error", "message": f"Expense Entry not found: {expense_name}"}

    # 2️⃣ Load credentials
    SERVICE_ACCOUNT_FILE = frappe.get_app_path(
        "accounts_manager", "google_sheets", "credentials.json"
    )
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        frappe.log_error(
            message=f"Credentials file not found: {SERVICE_ACCOUNT_FILE}",
            title="Google Sheets Auth Error"
        )
        return {"status": "error", "message": "Service account credentials missing."}

    try:
        credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()
    except Exception as e:
        frappe.log_error(message=str(e), title="Google Sheets Service Initialization Failed")
        return {"status": "error", "message": "Failed to initialize Google Sheets service."}

    # 3️⃣ Define headers and row values
    headers = ["Expense ID", "Expense Category", "Expense Type", "Posting Date", "Amount", "Description"]
    values = [[
        to_serializable(doc.name),
        to_serializable(getattr(doc, "expense_category", "")),
        to_serializable(doc.expense_type),
        to_serializable(doc.posting_date),
        to_serializable(doc.amount),
        to_serializable(doc.description)
    ]]

    try:
        # 4️⃣ Ensure headers exist in A1:F1
        existing_headers = sheet.values().get(spreadsheetId=spreadsheet_id, range=f"{sheet_name}!A1:F1").execute()
        if not existing_headers.get("values"):
            sheet.values().update(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet_name}!A1:F1",
                valueInputOption="RAW",
                body={"values": [headers]}
            ).execute()
            logger.info("Headers added to sheet.")

        # 5️⃣ Check for duplicates in column A (Expense ID)
        existing_ids_data = sheet.values().get(spreadsheetId=spreadsheet_id, range=f"{sheet_name}!A2:A").execute()
        existing_ids = [row[0] for row in existing_ids_data.get("values", []) if row]
        if doc.name in existing_ids:
            return {"status": "error", "message": f"Expense Entry {doc.name} is already pushed."}

        # 6️⃣ Append the row starting at column A, row 2
        result = sheet.values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A2",          # Always start appending at column A, row 2
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={'values': values}
        ).execute()

        updated_rows = result.get("updates", {}).get("updatedRows", 0)
        logger.info("Rows updated: %s", updated_rows)

        return {
            "status": "success",
            "expense_name": expense_name,
            "updated_rows": updated_rows,
            "spreadsheet_id": spreadsheet_id,
            "sheet_name": sheet_name
        }

    except Exception as e:
        frappe.log_error(message=str(e), title="Failed to push Expense Entry to Google Sheet")
        logger.error("Push error: %r", e, exc_info=True)
        return {"status": "error", "message": str(e)}
