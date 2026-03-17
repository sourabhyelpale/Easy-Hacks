import frappe


# ================= BULK STATUS UPDATE =================

@frappe.whitelist()
def bulk_update_docstatus(doctype, names, action):

    restricted = ["Sales Invoice", "Purchase Invoice", "Stock Entry"]

    if doctype in restricted:
        frappe.throw(f"{doctype} not allowed for force update")

    if isinstance(names, str):
        import json
        names = json.loads(names)

    success = []
    failed = []

    meta = frappe.get_meta(doctype)

    for name in names:
        try:
            doc = frappe.get_doc(doctype, name)

            # ================= SUBMITTABLE =================
            if meta.is_submittable:

                # -------- SUBMIT --------
                if action == "submit":

                    if doc.docstatus == 0:
                        doc.submit()

                    elif doc.docstatus == 2:
                        # Cancelled → Draft → Submit
                        frappe.db.set_value(doctype, name, "docstatus", 0)
                        frappe.db.commit()
                        doc.reload()
                        doc.submit()

                    else:
                        failed.append(f"{name} (Already Submitted)")
                        continue

                # -------- CANCEL --------
                elif action == "cancel":

                    if doc.docstatus == 1:
                        doc.cancel()
                    else:
                        failed.append(f"{name} (Not Submitted)")
                        continue

                # -------- DRAFT --------
                elif action == "draft":

                    if doc.docstatus == 1:
                        # Submitted → Cancel first
                        doc.cancel()

                    # Force to Draft (works for both 1 & 2)
                    frappe.db.set_value(doctype, name, "docstatus", 0)
                    frappe.db.commit()

                success.append(name)

            # ================= MASTER DOCTYPES =================
            else:

                if action in ["submit", "cancel"]:
                    failed.append(f"{name} (Not Submittable)")
                    continue

                elif action == "draft":
                    frappe.db.set_value(doctype, name, "docstatus", 0)
                    frappe.db.commit()
                    success.append(name)

        except Exception:
            failed.append(name)
            frappe.log_error(
                frappe.get_traceback(),
                f"[Easy Hacks] Bulk Update Failed: {doctype} - {name}"
            )

    return {
        "success": success,
        "failed": failed
    }


# ================= BULK DELETE =================
@frappe.whitelist()
def bulk_delete_docs(doctype, names):

    if isinstance(names, str):
        import json
        names = json.loads(names)

    success = []
    failed = []

    for name in names:
        try:
            doc = frappe.get_doc(doctype, name)

            # If submitted → cancel first
            if doc.docstatus == 1:
                doc.cancel()

            # Delete document
            frappe.delete_doc(doctype, name, force=1)

            success.append(name)

        except Exception:
            failed.append(name)
            frappe.log_error(
                frappe.get_traceback(),
                f"[Easy Hacks] Bulk Delete Failed: {doctype} - {name}"
            )

    return {
        "success": success,
        "failed": failed
    }