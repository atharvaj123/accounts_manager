# Copyright (c) 2025, Atharva Joshi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from accounts_manager.google_sheets.auth import get_google_service

class ExpenseEntry(Document):
    
    def push_to_google_sheet(self):
        # No need to pass expense_name, use self
        service = get_google_service()

        spreadsheet_id = "1ybHL9ja9W20B9Nl1MFLgd9WEA132RqgKsNWiUWv1Yqs"
        sheet_name = "Sheet1"

        values = [[
            self.name,
            self.posting_date.strftime("%Y-%m-%d") if self.posting_date else "",
            self.description or "",
            self.expense_type or "",
            float(self.amount or 0)
        ]]

        body = {"values": values}

        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=sheet_name,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()

        return "OK"
