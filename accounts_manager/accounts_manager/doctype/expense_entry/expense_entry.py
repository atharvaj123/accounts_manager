# Copyright (c) 2025, Atharva Joshi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from accounts_manager.google_sheets.auth import get_google_service

class ExpenseEntry(Document):

    def push_to_google_sheet(self, spreadsheet_id=None, sheet_name=None):
        spreadsheet_id = spreadsheet_id or "1ybHL9ja9W20B9Nl1MFLgd9WEA132RqgKsNWiUWv1Yqs"
        sheet_name = sheet_name or "Sheet1"

        service = get_google_service()

        values = [[
            self.name or "",
            self.posting_date.strftime("%Y-%m-%d") if self.posting_date else "",
            self.description or "",
            self.expense_type or "",
            float(self.amount or 0)
        ]]

        body = {"values": values}

        try:
            result = service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=sheet_name,
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()
            frappe.log(f"Pushed ExpenseEntry {self.name} to Google Sheet, updated rows: {result.get('updates', {}).get('updatedRows')}")
            return {"status": "success", "updated_rows": result.get('updates', {}).get('updatedRows', 0)}

        except Exception as e:
            frappe.log_error(message=str(e), title="Failed to push ExpenseEntry to Google Sheet")
            raise frappe.ValidationError(f"Failed to push to Google Sheet: {str(e)}")
