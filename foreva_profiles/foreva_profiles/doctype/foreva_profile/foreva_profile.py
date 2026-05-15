import random
import string
from io import BytesIO

import frappe
from frappe.model.document import Document


def _generate_id(length):
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=length))


class ForevaProfile(Document):
    def before_insert(self):
        if not self.unique_id:
            self.unique_id = _generate_id(8)
        if not self.edit_token:
            self.edit_token = _generate_id(20)

    def after_insert(self):
        self._generate_qr()
        self._send_welcome_email()

    def _generate_qr(self):
        try:
            import qrcode
        except ImportError:
            frappe.log_error("qrcode not installed — skipping QR generation")
            return

        url = f"https://forevastore.com/p/{self.unique_id}"
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": f"qr_{self.unique_id}.png",
            "content": buffer.getvalue(),
            "attached_to_doctype": "Foreva Profile",
            "attached_to_name": self.name,
            "is_private": 0,
        })
        file_doc.insert(ignore_permissions=True)
        frappe.db.set_value("Foreva Profile", self.name, "qr_code", file_doc.file_url)

    def _send_welcome_email(self):
        if not self.customer_email:
            return

        name = self.customer_name or "there"
        edit_link = f"https://forevastore.com/edit/{self.unique_id}"

        frappe.sendmail(
            now=True,
            recipients=[self.customer_email],
            subject="Your Foreva tag is ready — set up your profile",
            message=f"""Hi {name},

Your Foreva tag is on its way!

Set up your profile so anyone who finds your belongings can reach you:

{edit_link}

It takes two minutes. Add your name, a message, and however you'd like to be contacted. You can update it anytime — the QR on your tag always shows the latest.

—
Team Foreva
forevastore.com

---
This link is personal to you. Don't share it.
""",
        )
