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

    # HIDE all Help dropdown items (hides the Help button entirely)
    for item in navbar.help_dropdown:
        item.hidden = 1

    # HIDE Toggle Theme from settings dropdown
    for item in navbar.settings_dropdown:
        if item.item_label == "Toggle Theme":
            item.hidden = 1

    navbar.save(ignore_permissions=True)

    # Set dark theme for all existing users (with retry for deadlock)
    try:
        frappe.db.sql("UPDATE `tabUser` SET desk_theme = 'Dark' WHERE desk_theme != 'Dark' OR desk_theme IS NULL")
    except Exception:
        pass  # Ignore deadlock errors on this non-critical update

    # Remove ERPNext UI items (ERPNext is not installed on this site)
    cleanup_erpnext_items()

    frappe.db.commit()

    # Clear cache so changes take effect
    frappe.clear_cache()


def cleanup_erpnext_items():
    """Remove ERPNext UI items - ERPNext is not installed on this site"""
    try:
        # Delete ERPNext desktop icons
        frappe.db.sql("""
            DELETE FROM `tabDesktop Icon` WHERE app = 'erpnext'
        """)

        # Delete ERPNext workspace sidebar items
        frappe.db.sql("""
            DELETE FROM `tabWorkspace Sidebar Item`
            WHERE parent IN (SELECT name FROM `tabWorkspace Sidebar` WHERE app = 'erpnext')
        """)

        # Delete ERPNext workspace sidebars
        frappe.db.sql("""
            DELETE FROM `tabWorkspace Sidebar` WHERE app = 'erpnext'
        """)

        # Delete ERPNext workspaces
        frappe.db.sql("""
            DELETE FROM `tabWorkspace` WHERE app = 'erpnext'
        """)
    except Exception:
        pass  # Ignore errors if tables don't exist yet
