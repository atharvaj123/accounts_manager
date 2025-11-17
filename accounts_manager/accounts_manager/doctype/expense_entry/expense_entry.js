// Copyright (c) 2025, Atharva Joshi and contributors
// For license information, please see license.txt

frappe.ui.form.on('Expense Entry', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            let btn = frm.add_custom_button(__('Push to Google Sheet'), function() {
                let spreadsheet_id = '1ybHL9ja9W20B9Nl1MFLgd9WEA132RqgKsNWiUWv1Yqs';
                btn.set_disabled(true);
                
                frappe.call({
                    method: "accounts_manager.google_sheets.sheet_sync.push_expense_to_sheet",
                    args: {
                        expense_name: frm.doc.name,
                        spreadsheet_id: spreadsheet_id,
                        sheet_name: 'Sheet1'
                    },
                    freeze: true,
                    freeze_message: 'Pushing to Google Sheet...',
                    callback: function(r) {
                        btn.set_disabled(false);
                        if (!r.exc && r.message.status == "success") {
                            frappe.msgprint(__('Pushed successfully'));
                        } else {
                            let msg = (r.exc && r.exc.message) ? r.exc.message : r.exc || "Unknown error";
                            frappe.msgprint(__('Error: {0}', [msg]));
                        }
                    },
                    error: function() {
                        btn.set_disabled(false);
                        frappe.msgprint(__('Failed to push to Google Sheet.'));
                    }
                });
            });
        }
    }
});


