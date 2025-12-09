import frappe


def extend_bootinfo(bootinfo):
    """Override ERPNext branding with Kraken in boot data"""
    kraken_logo = "/assets/kraken_theme/images/kraken-icon.png"

    # Rebrand all apps to show Kraken logo and name where ERPNext appears
    for app in bootinfo.get("app_data", []):
        if app.get("app_name") == "erpnext":
            app["app_title"] = "Kraken"
            app["app_logo_url"] = kraken_logo
        elif app.get("app_name") == "frappe":
            # Also rebrand Frappe to Kraken for consistency
            app["app_title"] = "Kraken"
            app["app_logo_url"] = kraken_logo

    # Ensure the first app (shown in navbar) uses Kraken branding
    if bootinfo.get("app_data"):
        bootinfo["app_data"][0]["app_logo_url"] = kraken_logo
        bootinfo["app_data"][0]["app_title"] = "Kraken"
