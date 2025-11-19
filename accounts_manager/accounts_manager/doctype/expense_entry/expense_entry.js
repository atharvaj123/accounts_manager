// Copyright (c) 2025, Atharva Joshi and contributors
// For license information, please see license.txt

frappe.ui.form.on('Expense Entry', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            let btn = frm.add_custom_button(__('Push to Google Sheet'), function() {
                btn.prop('disabled', true);  // Disable button during API call

                frappe.call({
                    method: "accounts_manager.google_sheets.sheet_sync.push_expense_to_sheet",
                    args: {
                        expense_name: frm.doc.name,
                        spreadsheet_id: '1ybHL9ja9W20B9Nl1MFLgd9WEA132RqgKsNWiUWv1Yqs',
                        sheet_name: 'Sheet1'
                    },
                    freeze: true,
                    freeze_message: 'Pushing to Google Sheet...',
                    callback: function(r) {
                        btn.prop('disabled', false);  // Re-enable button
                        if (!r.exc && r.message && r.message.status === "success") {
                            frappe.msgprint(__('Pushed successfully'));
                        } else {
                            let msg = "Unknown error";
                            if (r.exc && r.exc.message) {
                                msg = r.exc.message;
                            } else if (r.message && r.message.message) {
                                msg = r.message.message;
                            }
                            frappe.msgprint(__('Error: {0}', [msg]));
                        }
                    },
                    error: function() {
                        btn.prop('disabled', false);
                        frappe.msgprint(__('Failed to push to Google Sheet.'));
                    }
                });
            });
        }
    }
});
