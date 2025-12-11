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

    # Fix navbar dropdown items (runs after sync_standard_items)
    navbar = frappe.get_doc("Navbar Settings")

    # DELETE all Help dropdown items (hides the Help button entirely)
    navbar.help_dropdown = []

    # DELETE Toggle Theme from settings dropdown
    navbar.settings_dropdown = [i for i in navbar.settings_dropdown if i.item_label != "Toggle Theme"]

    navbar.save(ignore_permissions=True)

    # Set dark theme for all existing users (with retry for deadlock)
    try:
        frappe.db.sql("UPDATE `tabUser` SET desk_theme = 'Dark' WHERE desk_theme != 'Dark' OR desk_theme IS NULL")
    except Exception:
        pass  # Ignore deadlock errors on this non-critical update

    frappe.db.commit()

    # Clear cache so changes take effect
    frappe.clear_cache()


def set_dark_theme_for_new_user(doc, method=None):
    """Set dark theme for newly created users"""
    if not doc.desk_theme or doc.desk_theme != "Dark":
        doc.desk_theme = "Dark"
