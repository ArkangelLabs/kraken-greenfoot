import frappe

def hide_erpnext():
    """Return False to hide ERPNext from users with Warranties Only profile"""
    if frappe.session.user == "Guest":
        return True
    user = frappe.get_doc("User", frappe.session.user)
    # Hide ERPNext if user has Warranties Only module profile
    if user.module_profile == "Warranties Only":
        return False
    return True
