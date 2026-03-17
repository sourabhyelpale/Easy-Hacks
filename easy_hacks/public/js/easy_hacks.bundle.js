console.log("EASY HACKS LOADED ✅");

// Run on every route change
frappe.router.on('change', () => {

    if (frappe.get_route()[0] === 'List') {

        setTimeout(() => {
            let listview = cur_list;

            if (!listview || listview.easy_hacks_added) return;

            listview.easy_hacks_added = true;

            console.log("ADDING BULK ACTION BUTTONS");

            // Actions
            listview.page.add_action_item(__('Submit'), () => bulk_action(listview, 'submit'));
            listview.page.add_action_item(__('Cancel'), () => bulk_action(listview, 'cancel'));
            listview.page.add_action_item(__('Draft'), () => bulk_action(listview, 'draft'));
            listview.page.add_action_item(__('Delete Records'), () => bulk_delete(listview));

        }, 800);
    }
});


// ================= BULK STATUS UPDATE =================
function bulk_action(listview, action) {

    let selected = listview.get_checked_items();

    if (!selected.length) {
        frappe.msgprint("Please select records");
        return;
    }

    frappe.confirm(
        `Are you sure you want to ${action} ${selected.length} records?`,
        () => {

            frappe.dom.freeze("Processing...");

            frappe.call({
                method: "easy_hacks.api.bulk_update_docstatus",
                args: {
                    doctype: listview.doctype,
                    names: selected.map(d => d.name),
                    action: action
                },
                callback: function (r) {

                    frappe.dom.unfreeze();

                    let msg = "Done!";
                    if (r.message) {
                        msg = `Success: ${r.message.success.length}, Failed: ${r.message.failed.length}`;
                    }

                    frappe.msgprint(msg);
                    listview.refresh();
                }
            });
        }
    );
}


// ================= BULK DELETE =================
function bulk_delete(listview) {

    let selected = listview.get_checked_items();

    if (!selected.length) {
        frappe.msgprint("Please select records");
        return;
    }

    frappe.confirm(
        `Submitted records will be cancelled before deletion.\nDelete ${selected.length} records?`,
        () => {

            frappe.dom.freeze("Deleting...");

            frappe.call({
                method: "easy_hacks.api.bulk_delete_docs",
                args: {
                    doctype: listview.doctype,
                    names: selected.map(d => d.name)
                },
                callback: function (r) {

                    frappe.dom.unfreeze();

                    let msg = "Deleted!";
                    if (r.message) {
                        msg = `Deleted: ${r.message.success.length}, Failed: ${r.message.failed.length}`;
                    }

                    frappe.msgprint(msg);
                    listview.refresh();
                }
            });
        }
    );
}