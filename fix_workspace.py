import frappe

def run():
    frappe.set_user("Administrator")

    rows = frappe.db.sql("SELECT name, is_standard, is_public, is_default, module FROM `tabWorkspace`", as_dict=True)
    print("Current workspaces:", rows)

    frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name=%s", ("Foreva Profiles",))
    frappe.db.sql("DELETE FROM `tabWorkspace Shortcut` WHERE parent=%s", ("Foreva Profiles",))
    frappe.db.commit()
    print("Cleaned old record")

    doc = frappe.get_doc({
        "doctype": "Workspace",
        "name": "Foreva Profiles",
        "label": "Foreva Profiles",
        "module": "Foreva Profiles",
        "is_standard": 1,
        "is_default": 1,
        "is_public": 1,
        "content": '[{"type":"header","data":{"text":"Foreva","level":4,"col":12}},{"type":"shortcut","data":{"shortcut_name":"Foreva Profile","col":3}}]',
        "shortcuts": [{
            "doctype": "Workspace Shortcut",
            "type": "DocType",
            "label": "Foreva Profile",
            "link_to": "Foreva Profile",
            "color": "Green",
        }]
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    print("Workspace created with is_public=1")

    result = frappe.db.sql("SELECT name, is_standard, is_public, is_default, module FROM `tabWorkspace` WHERE name=%s", ("Foreva Profiles",), as_dict=True)
    print("Verified:", result)
