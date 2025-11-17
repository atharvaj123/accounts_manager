# Copyright (c) 2025, Atharva Joshi and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime

def track_history(doc, method):
    # Skip if new document
    if doc.get("__islocal"):
        return

    try:
        old_doc = frappe.get_doc(doc.doctype, doc.name)
    except frappe.DoesNotExistError:
        # Old document not found, likely new doc
        return

    if not old_doc:
        return

    changes = []
    monitor_fields = ["description", "amount", "posting_date", "expense_type", "remarks"]

    for f in monitor_fields:
        old_val = getattr(old_doc, f, None)
        new_val = getattr(doc, f, None)
        if (old_val or "") != (new_val or ""):
            changes.append((f, old_val, new_val))

    old_tags = [t.tag for t in old_doc.get("tags") or []]
    new_tags = [t.tag for t in doc.get("tags") or []]
    if old_tags != new_tags:
        changes.append(("tags", ", ".join(old_tags), ", ".join(new_tags)))

    for field_name, old_value, new_value in changes:
        doc.append("history", {
            "changed_on": now_datetime(),
            "changed_by": frappe.session.user,
            "field_name": field_name,
            "old_value": frappe.as_json(old_value) if isinstance(old_value, (list, dict)) else (old_value or ""),
            "new_value": frappe.as_json(new_value) if isinstance(new_value, (list, dict)) else (new_value or ""),
            "notes": ""
        })
