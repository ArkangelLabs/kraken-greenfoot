#!/usr/bin/env python3
"""
Script to import equipment and warranty registrations from Supabase data.
Run with: bench --site dev.localhost execute warranties.import_data.import_all
"""

import frappe

# Asset type mapping from Supabase integers to Frappe select options
ASSET_TYPE_MAP = {
    1: "HVAC",
    2: "Heat Pump",
    8: "Ventilation"
}


def import_equipment_batch(data_batch):
    """Import a batch of equipment registrations"""
    created = 0
    skipped = 0
    errors = []

    for item in data_batch:
        try:
            # Check if already imported by job_asset_id
            if item.get("job_asset_id"):
                existing = frappe.db.exists("Equipment Registration", {"job_asset_id": item.get("job_asset_id")})
                if existing:
                    skipped += 1
                    continue

            # Check if brand exists, set to None if not a valid manufacturer
            brand = item.get('brand')
            if brand and not frappe.db.exists("HVAC Manufacturer", brand):
                brand = None

            # Map asset_type from integer to string
            asset_type = item.get("asset_type")
            if isinstance(asset_type, int):
                asset_type = ASSET_TYPE_MAP.get(asset_type)

            # Normalize province to uppercase
            province = item.get("province", "")
            if province:
                province = province.upper()
                # Handle "Unknown" values
                if province == "UNKNOWN":
                    province = None

            doc = frappe.get_doc({
                "doctype": "Equipment Registration",
                "job_asset_id": item.get("job_asset_id"),
                "job_number": item.get("job_number"),
                "job_address": item.get("job_address"),
                "city": item.get("city"),
                "province": province,
                "postal_code": item.get("postal_code"),
                "brand": brand,
                "indoor_model": item.get("indoor_model"),
                "indoor_serial": item.get("indoor_serial"),
                "outdoor_model": item.get("outdoor_model"),
                "outdoor_serial": item.get("outdoor_serial"),
                "install_date": item.get("install_date"),
                "asset_type": asset_type,
                "customer_first_name": item.get("customer_first_name"),
                "customer_last_name": item.get("customer_last_name"),
                "customer_email": item.get("customer_email"),
                "customer_phone": item.get("customer_phone"),
                "contact_role": item.get("contact_role"),
            })
            doc.insert(ignore_permissions=True)
            created += 1
        except Exception as e:
            errors.append({"job_asset_id": item.get("job_asset_id"), "error": str(e)})

    frappe.db.commit()
    return created, skipped, errors


def import_from_json(json_data):
    """Import equipment registrations from JSON data"""
    import json
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    return import_equipment_batch(data)


def import_all():
    """Main import function - placeholder for sample data"""
    print("To import data, use:")
    print("  bench --site dev.localhost execute warranties.import_data.import_from_json --args '[{...}]'")
    print("Or use the REST API: POST /api/method/warranties.api.bulk_import_equipment")
    return {"message": "Use import_from_json with your data"}
