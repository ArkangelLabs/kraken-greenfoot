# Copyright (c) 2025, Kraken and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.password import get_decrypted_password


class BrandCredentials(Document):
    pass


def get_brand_credentials(brand: str) -> dict:
    """Get credentials for a brand.
    
    Args:
        brand: Brand key (ge, mitsubishi, lg, fujitsu)
        
    Returns:
        dict with username and password, or empty dict if not configured
    """
    brand = brand.lower().replace(" ", "_").replace("-", "_")
    
    # Map common brand names to field prefixes
    brand_map = {
        "ge": "ge",
        "ge_hvac": "ge",
        "mitsubishi": "mitsubishi",
        "mesca": "mitsubishi",
        "lg": "lg",
        "fujitsu": "fujitsu",
    }
    
    field_prefix = brand_map.get(brand, brand)
    
    try:
        doc = frappe.get_single("Brand Credentials")
        username = getattr(doc, f"{field_prefix}_username", None)
        
        if not username:
            return {}
            
        password = get_decrypted_password(
            "Brand Credentials",
            "Brand Credentials",
            f"{field_prefix}_password"
        )
        
        return {
            "username": username,
            "password": password or ""
        }
    except Exception:
        return {}


@frappe.whitelist()
def test_brand_login(brand: str) -> dict:
    """Test if credentials are configured for a brand.
    
    Args:
        brand: Brand key (ge, mitsubishi, lg, fujitsu)
        
    Returns:
        dict with configured status
    """
    creds = get_brand_credentials(brand)
    
    return {
        "brand": brand,
        "configured": bool(creds.get("username") and creds.get("password")),
        "username": creds.get("username", "")
    }
