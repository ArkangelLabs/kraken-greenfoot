"""
Migration script to import all data from Supabase into Frappe.
Run with: bench --site dev.localhost execute warranties.migrate_from_supabase.migrate_all
"""

import frappe
from frappe.utils import now_datetime

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

# Province normalization (uppercase)
def normalize_province(province):
    if not province:
        return None
    return province.upper().strip()


def get_valid_brands():
    """Get list of valid brand names from HVAC Manufacturer"""
    return [d.brand for d in frappe.get_all("HVAC Manufacturer", fields=["brand"])]


def migrate_equipment_registrations(records):
    """Import equipment registration records"""
    valid_brands = get_valid_brands()
    imported = 0
    skipped = 0
    errors = []

    for record in records:
        try:
            # Check if already exists by job_asset_id
            existing = frappe.db.exists("Equipment Registration", {"job_asset_id": record.get("job_asset_id")})
            if existing:
                skipped += 1
                continue

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
            imported += 1

            # Commit every 50 records to avoid memory issues
            if imported % 50 == 0:
                frappe.db.commit()
                print(f"Imported {imported} equipment registrations...")

        except Exception as e:
            errors.append({"job_asset_id": record.get("job_asset_id"), "error": str(e)})

    frappe.db.commit()
    return {"imported": imported, "skipped": skipped, "errors": errors}


def migrate_warranty_registrations(records):
    """Import warranty registration records"""
    valid_brands = get_valid_brands()
    imported = 0
    skipped = 0
    errors = []

    for record in records:
        try:
            # Check if already exists by checking unique fields
            # Since warranties don't have a unique ID from Supabase, we check by serial
            serial = record.get("serial")
            if serial:
                existing = frappe.db.exists("Warranty Registration", {"serial": serial})
                if existing:
                    skipped += 1
                    continue

            # Normalize brand
            brand = record.get("brand")
            if brand and brand not in valid_brands:
                brand = None

            # Map processing status
            status_map = {
                "pending": "Pending",
                "processing": "Processing",
                "completed": "Completed",
                "failed": "Failed"
            }
            processing_status = record.get("processing_status", "pending")
            if processing_status:
                processing_status = status_map.get(processing_status.lower(), "Pending")
            else:
                processing_status = "Pending"

            doc = frappe.get_doc({
                "doctype": "Warranty Registration",
                "registering_as": record.get("registering_as", "Contractor"),
                "install_date": record.get("install_date"),
                "installation_type": record.get("installation_type"),
                "purchase_date": record.get("purchase_date"),
                "dealer_id": record.get("dealer_id"),
                "brand": brand,
                "model": record.get("model"),
                "serial": serial,
                "model1": record.get("model1"),
                "serial1": record.get("serial1"),
                "model2": record.get("model2"),
                "serial2": record.get("serial2"),
                "model3": record.get("model3"),
                "serial3": record.get("serial3"),
                "model4": record.get("model4"),
                "serial4": record.get("serial4"),
                "model5": record.get("model5"),
                "serial5": record.get("serial5"),
                "model6": record.get("model6"),
                "serial6": record.get("serial6"),
                "model7": record.get("model7"),
                "serial7": record.get("serial7"),
                "model8": record.get("model8"),
                "serial8": record.get("serial8"),
                "model9": record.get("model9"),
                "serial9": record.get("serial9"),
                "owner_first_name": record.get("owner_first_name"),
                "owner_last_name": record.get("owner_last_name"),
                "owner_email": record.get("owner_email"),
                "owner_phone": record.get("owner_phone"),
                "owner_address": record.get("owner_address"),
                "owner_city": record.get("owner_city"),
                "owner_state": record.get("owner_state"),
                "owner_zip": record.get("owner_zip"),
                "contractor_name": record.get("contractor_name"),
                "contractor_email": record.get("contractor_email"),
                "contractor_phone": record.get("contractor_phone"),
                "contractor_address": record.get("contractor_address"),
                "contractor_city": record.get("contractor_city"),
                "contractor_state": record.get("contractor_state"),
                "contractor_zip": record.get("contractor_zip"),
                "processing_status": processing_status,
                "pdf_url": record.get("pdf_url"),
                "error_message": record.get("error_message"),
                "processed_at": record.get("processed_at"),
            })
            doc.insert(ignore_permissions=True)
            imported += 1

        except Exception as e:
            errors.append({"serial": record.get("serial"), "error": str(e)})

    frappe.db.commit()
    return {"imported": imported, "skipped": skipped, "errors": errors}


def migrate_all():
    """
    Main migration function - call this from bench execute.
    Note: This expects data to be passed via frappe.flags or run interactively.
    For MCP-based migration, use the API endpoints instead.
    """
    print("Migration script loaded. Use API endpoints for MCP-based migration.")
    print("Or call migrate_equipment_registrations(records) directly with data.")


@frappe.whitelist()
def import_equipment_batch(records):
    """
    API endpoint to import a batch of equipment registrations.
    Called from external systems with JSON data.
    """
    if isinstance(records, str):
        import json
        records = json.loads(records)

    result = migrate_equipment_registrations(records)
    return result


@frappe.whitelist()
def import_warranty_batch(records):
    """
    API endpoint to import a batch of warranty registrations.
    Called from external systems with JSON data.
    """
    if isinstance(records, str):
        import json
        records = json.loads(records)

    result = migrate_warranty_registrations(records)
    return result


@frappe.whitelist()
def get_migration_status():
    """Get current migration status - counts of records"""
    return {
        "equipment_registrations": frappe.db.count("Equipment Registration"),
        "warranty_registrations": frappe.db.count("Warranty Registration"),
        "hvac_manufacturers": frappe.db.count("HVAC Manufacturer"),
        "agent_logs": frappe.db.count("Agent Log")
    }
