import frappe

def check_app_permission():
    """Override ERPNext app permission - hide from Warranties Only users"""
    if frappe.session.user == "Administrator":
        return True
    
    # Hide from Website Users
    user_type = frappe.db.get_value("User", frappe.session.user, "user_type")
    if user_type == "Website User":
        return False
    
    # Hide from users with Warranties Only module profile
    module_profile = frappe.db.get_value("User", frappe.session.user, "module_profile")
    if module_profile == "Warranties Only":
        return False
    
    return True
