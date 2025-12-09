import frappe


def after_install():
    """Apply Kraken branding after app installation"""
    apply_kraken_branding()


def after_migrate():
    """Ensure Kraken branding is applied after migrations"""
    apply_kraken_branding()


def apply_kraken_branding():
    """Apply Kraken branding to settings using db_set to avoid validation issues"""
    # Update System Settings directly (avoids mandatory field validation)
    frappe.db.set_single_value("System Settings", "app_name", "Kraken")

    # Update Website Settings
    frappe.db.set_single_value("Website Settings", "app_name", "Kraken")
    frappe.db.set_single_value("Website Settings", "favicon", "/assets/kraken_theme/images/kraken-icon.png")
    frappe.db.set_single_value("Website Settings", "splash_image", "/assets/kraken_theme/images/kraken-icon.png")
    frappe.db.set_single_value("Website Settings", "footer_powered", "Powered by Kraken")

    # Update Navbar Settings
    frappe.db.set_single_value("Navbar Settings", "app_logo", "/assets/kraken_theme/images/kraken-icon.png")

    # Set dark theme for all existing users
    frappe.db.sql("UPDATE `tabUser` SET desk_theme = 'Dark' WHERE desk_theme != 'Dark' OR desk_theme IS NULL")

    frappe.db.commit()

    # Clear cache so changes take effect
    frappe.clear_cache()
