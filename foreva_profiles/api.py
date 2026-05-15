import re
import random
import string

import frappe


def _generate_id(length):
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=length))


def _get_profile(identifier):
    """Look up by unique_id first, then username."""
    names = frappe.get_all("Foreva Profile", filters={"unique_id": identifier}, limit=1)
    if not names:
        names = frappe.get_all("Foreva Profile", filters={"username": identifier}, limit=1)
    if not names:
        frappe.throw("Profile not found", frappe.DoesNotExistError)
    return frappe.get_doc("Foreva Profile", names[0].name)


@frappe.whitelist(allow_guest=True)
def get_profile(unique_id):
    profile = _get_profile(unique_id)
    return {
        "name_display": profile.name_display,
        "custom_message": profile.custom_message,
        "phone_display": profile.phone_display if profile.phone_visible else None,
        "phone_visible": bool(profile.phone_visible),
        "whatsapp": profile.whatsapp,
        "emergency_name": profile.emergency_name,
        "emergency_phone": profile.emergency_phone,
        "instagram": profile.instagram,
        "activated": bool(profile.activated),
        "username": profile.username or None,
    }


@frappe.whitelist(allow_guest=True)
def send_otp(unique_id, email):
    profile = _get_profile(unique_id)
    if profile.customer_email != email:
        frappe.throw("Email does not match our records")

    otp = "".join(random.choices(string.digits, k=6))
    frappe.cache().set_value(f"foreva_otp_{profile.unique_id}", otp, expires_in_sec=600)

    frappe.sendmail(
        now=True,
        recipients=[email],
        subject="Your Foreva Profile Access Code",
        message=f"""Hi {profile.customer_name or "there"},

Your one-time code to access your Foreva profile:

    {otp}

This code expires in 10 minutes.

— Team Foreva
forevastore.com""",
    )
    return "sent"


@frappe.whitelist(allow_guest=True)
def verify_otp(unique_id, otp):
    profile = _get_profile(unique_id)
    stored = frappe.cache().get_value(f"foreva_otp_{profile.unique_id}")
    if not stored or stored != otp:
        frappe.throw("Invalid or expired code")

    frappe.cache().delete_value(f"foreva_otp_{profile.unique_id}")
    session_token = _generate_id(32)
    frappe.cache().set_value(f"foreva_session_{profile.unique_id}", session_token, expires_in_sec=2592000)
    return session_token


@frappe.whitelist(allow_guest=True)
def update_profile(unique_id, session_token, **kwargs):
    profile = _get_profile(unique_id)
    stored = frappe.cache().get_value(f"foreva_session_{profile.unique_id}")
    if not stored or stored != session_token:
        frappe.throw("Invalid or expired session")

    # Validate username if provided
    new_username = kwargs.get("username", "").strip().lower()
    if new_username:
        if not re.match(r'^[a-z0-9][a-z0-9\-]{2,29}$', new_username):
            frappe.throw("Username must be 3–30 characters: letters, numbers, hyphens only. Cannot start with a hyphen.")
        existing = frappe.get_all("Foreva Profile", filters={"username": new_username}, limit=1)
        if existing and existing[0].name != profile.name:
            frappe.throw("That username is already taken.")
        profile.username = new_username
    elif "username" in kwargs and not new_username:
        profile.username = ""

    allowed = [
        "name_display", "custom_message",
        "phone_display", "phone_visible",
        "whatsapp", "emergency_name", "emergency_phone",
        "instagram",
    ]
    for field in allowed:
        if field in kwargs:
            setattr(profile, field, kwargs[field])

    profile.activated = 1
    profile.save(ignore_permissions=True)
    return profile.username or profile.unique_id
