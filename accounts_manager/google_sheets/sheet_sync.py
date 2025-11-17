from datetime import date, datetime
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import frappe

# Path to your Google Service Account JSON file
SERVICE_ACCOUNT_FILE = "path_to_your_service_account.json"  # Replace with actual path
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def to_serializable(obj):
    """Convert date or datetime to ISO format string for JSON serialization."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    return obj

@frappe.whitelist()
def push_expense_to_sheet(expense_name, spreadsheet_id, sheet_name):
    """
    Push Expense Entry to Google Sheet.
    """
    # Get the expense document
    doc = frappe.get_doc("Expense Entry", expense_name)

    # Prepare values to push
    values = [
        [
            to_serializable(doc.posting_date),
            doc.expense_type or "",
            float(doc.amount or 0),
            doc.description or "",
            doc.expense_category or "",
            doc.payment_mode or "",
            doc.reference or ""
        ]
    ]

    # Authenticate and create service
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    # Append values to the sheet
    body = {"values": values}

    result = sheet.values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()

    return {"status": "success", "updated_rows": result.get("updates", {}).get("updatedRows", 0)}
