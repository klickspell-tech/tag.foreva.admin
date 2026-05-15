import frappe


def create_test_profile():
    doc = frappe.get_doc({
        'doctype': 'Foreva Profile',
        'customer_name': 'Test User',
        'customer_email': 'test@example.com',
        'order_reference': 'TEST-001',
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    print('name:', doc.name)
    print('unique_id:', doc.unique_id)
    print('qr_code:', doc.qr_code)
