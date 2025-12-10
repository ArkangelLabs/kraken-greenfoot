import frappe


def extend_bootinfo(bootinfo):
    """Override all app branding with Kraken in boot data"""
    kraken_logo = "/assets/kraken_theme/images/kraken-icon.png"

    # Override ALL apps to use Kraken logo
    for app in bootinfo.get("app_data", []):
        # Fix app_logo_url - it may be a list, extract first value
        if isinstance(app.get("app_logo_url"), list):
            app["app_logo_url"] = kraken_logo
        else:
            app["app_logo_url"] = kraken_logo

        # Rebrand erpnext and frappe app titles
        if app.get("app_name") in ("erpnext", "frappe"):
            app["app_title"] = "Kraken"

    # Ensure the first app (shown in navbar/sidebar) uses Kraken branding
    if bootinfo.get("app_data"):
        bootinfo["app_data"][0]["app_logo_url"] = kraken_logo
        bootinfo["app_data"][0]["app_title"] = "Kraken"

    # Also override the global app_logo_url
    bootinfo["app_logo_url"] = kraken_logo
