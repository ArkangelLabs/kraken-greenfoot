"""
Direct import script that takes JSON data and imports it into Frappe.
Usage: bench --site dev.localhost execute warranties.import_from_supabase.import_records --args '{"data": [...]}'
"""

import frappe
import json

# Asset type mapping from Supabase integers to Frappe Select options
ASSET_TYPE_MAP = {
    1: "HVAC",
    2: "Heat Pump",
    8: "Ventilation"
}

# Contact role normalization
CONTACT_ROLE_MAP = {
    "Job Contact": "Job Contact",
    "Property Owner": "Property Owner",
    "Homeowner": "Property Owner",
    "Building Owner": "Property Owner",
    "Facility Manager": "Property Owner",
    "Property Manager": "Property Owner",
    "Billing Contact": "Property Owner",
}

def normalize_province(province):
    if not province:
        return None
    return province.upper().strip()


def get_valid_brands():
    """Get list of valid brand names from HVAC Manufacturer"""
    return [d.brand for d in frappe.get_all("HVAC Manufacturer", fields=["brand"])]


def import_equipment_record(record, valid_brands):
    """Import a single equipment registration record"""
    try:
        # Check if already exists by job_asset_id
        existing = frappe.db.exists("Equipment Registration", {"job_asset_id": record.get("job_asset_id")})
        if existing:
            return {"status": "skipped", "job_asset_id": record.get("job_asset_id")}

        # Normalize brand - only use if it matches a valid manufacturer
        brand = record.get("brand")
        if brand and brand not in valid_brands:
            brand = None  # Clear invalid brands

        # Normalize asset type
        asset_type_raw = record.get("asset_type")
        asset_type = ASSET_TYPE_MAP.get(asset_type_raw, "HVAC")

        # Normalize contact role
        contact_role_raw = record.get("contact_role", "")
        contact_role = CONTACT_ROLE_MAP.get(contact_role_raw, "Job Contact")

        # Normalize province
        province = normalize_province(record.get("province"))

        doc = frappe.get_doc({
            "doctype": "Equipment Registration",
            "job_asset_id": record.get("job_asset_id"),
            "job_number": record.get("job_number"),
            "job_address": record.get("job_address"),
            "city": record.get("city"),
            "province": province,
            "postal_code": record.get("postal_code"),
            "brand": brand,
            "indoor_model": record.get("indoor_model"),
            "indoor_serial": record.get("indoor_serial"),
            "outdoor_model": record.get("outdoor_model"),
            "outdoor_serial": record.get("outdoor_serial"),
            "install_date": record.get("install_date"),
            "asset_type": asset_type,
            "customer_first_name": record.get("customer_first_name"),
            "customer_last_name": record.get("customer_last_name"),
            "customer_email": record.get("customer_email"),
            "customer_phone": record.get("customer_phone"),
            "contact_role": contact_role,
        })
        doc.insert(ignore_permissions=True)
        return {"status": "imported", "job_asset_id": record.get("job_asset_id"), "name": doc.name}

    except Exception as e:
        return {"status": "error", "job_asset_id": record.get("job_asset_id"), "error": str(e)}


def import_records(data):
    """
    Import equipment registration records from JSON data.
    Args:
        data: List of record dictionaries or JSON string
    """
    if isinstance(data, str):
        data = json.loads(data)

    valid_brands = get_valid_brands()

    imported = 0
    skipped = 0
    errors = []

    for i, record in enumerate(data):
        result = import_equipment_record(record, valid_brands)

        if result["status"] == "imported":
            imported += 1
        elif result["status"] == "skipped":
            skipped += 1
        else:
            errors.append(result)

        # Commit every 50 records
        if (i + 1) % 50 == 0:
            frappe.db.commit()
            print(f"Processed {i + 1} records... (imported: {imported}, skipped: {skipped})")

    frappe.db.commit()

    print(f"\n=== Import Complete ===")
    print(f"Total processed: {len(data)}")
    print(f"Imported: {imported}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {len(errors)}")

    if errors:
        print("\nErrors:")
        for err in errors[:10]:  # Show first 10 errors
            print(f"  - job_asset_id {err.get('job_asset_id')}: {err.get('error')}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")

    return {
        "imported": imported,
        "skipped": skipped,
        "errors": errors
    }


def import_from_file(filepath):
    """Import records from a JSON file"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    return import_records(data)
