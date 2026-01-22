"""
Import CSV files from Supabase export into Frappe.
Usage: bench --site dev.localhost execute warranties.import_csv.import_all
"""

import frappe
import csv
from frappe.utils import getdate

# Asset type mapping from Supabase integers to Frappe Select options
ASSET_TYPE_MAP = {
    "1": "HVAC",
    "2": "Heat Pump",
    "8": "Ventilation",
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

# Processing status normalization
STATUS_MAP = {
    "pending": "Pending",
    "processing": "Processing",
    "completed": "Completed",
    "failed": "Failed",
    "Pending": "Pending",
    "Processing": "Processing",
    "Completed": "Completed",
    "Failed": "Failed",
}


def normalize_province(province):
    if not province:
        return None
    province = province.upper().strip()
    # Handle invalid provinces
    if province == "UNKNOWN" or province not in ["AB", "BC", "MB", "NB", "NL", "NS", "NT", "NU", "ON", "PE", "QC", "SK", "YT"]:
        return None
    return province


def clean_email(email):
    """Clean and validate email - return None if invalid"""
    if not email:
        return None
    email = email.strip()
    # Handle common invalid patterns
    if email.upper() == "NO EMAIL" or email.upper() == "N/A":
        return None
    # Handle multiple emails - take first one
    if "/" in email:
        email = email.split("/")[0].strip()
    if " " in email:
        email = email.split()[0].strip()
    # Basic validation
    if "@" not in email or "." not in email:
        return None
    return email


def clean_phone(phone):
    """Clean phone number - return None if invalid"""
    if not phone:
        return None
    phone = phone.strip()
    # Remove trailing letters/notes
    import re
    phone = re.sub(r'\s+[A-Za-z].*$', '', phone)
    return phone if phone else None


def normalize_registering_as(value):
    """Normalize registering_as field"""
    if not value:
        return "Contractor"
    value = value.strip()
    if "dealer" in value.lower() or "partner" in value.lower() or "pro solution" in value.lower():
        return "Contractor"
    if "homeowner" in value.lower():
        return "Homeowner"
    if "contractor" in value.lower():
        return "Contractor"
    return "Contractor"


def get_valid_brands():
    """Get list of valid brand names from HVAC Manufacturer"""
    return [d.brand for d in frappe.get_all("HVAC Manufacturer", fields=["brand"])]


def import_equipment_registrations(csv_path="/workspace/development/equipment_registrations_rows.csv"):
    """Import equipment registrations from CSV"""
    valid_brands = get_valid_brands()
    imported = 0
    skipped = 0
    errors = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader):
            try:
                job_asset_id = row.get('job_asset_id')

                # Check if already exists
                if frappe.db.exists("Equipment Registration", {"job_asset_id": job_asset_id}):
                    skipped += 1
                    continue

                # Normalize brand
                brand = row.get('brand')
                if brand and brand not in valid_brands:
                    brand = None

                # Normalize asset type
                asset_type_raw = row.get('asset_type')
                asset_type = ASSET_TYPE_MAP.get(asset_type_raw, "HVAC")

                # Normalize contact role
                contact_role_raw = row.get('contact_role', '')
                contact_role = CONTACT_ROLE_MAP.get(contact_role_raw, "Job Contact")

                # Normalize province
                province = normalize_province(row.get('province'))

                # Parse install date
                install_date = row.get('install_date')
                if install_date:
                    try:
                        install_date = getdate(install_date)
                    except:
                        install_date = None

                doc = frappe.get_doc({
                    "doctype": "Equipment Registration",
                    "job_asset_id": int(job_asset_id) if job_asset_id else None,
                    "job_number": int(row.get('job_number')) if row.get('job_number') else None,
                    "job_address": row.get('job_address'),
                    "city": row.get('city'),
                    "province": province,
                    "postal_code": row.get('postal_code') or None,
                    "brand": brand,
                    "indoor_model": row.get('indoor_model'),
                    "indoor_serial": row.get('indoor_serial'),
                    "outdoor_model": row.get('outdoor_model'),
                    "outdoor_serial": row.get('outdoor_serial'),
                    "install_date": install_date,
                    "asset_type": asset_type,
                    "customer_first_name": row.get('customer_first_name'),
                    "customer_last_name": row.get('customer_last_name'),
                    "customer_email": clean_email(row.get('customer_email')),
                    "customer_phone": clean_phone(row.get('customer_phone')),
                    "contact_role": contact_role,
                })
                doc.insert(ignore_permissions=True)
                imported += 1

                # Commit every 100 records
                if imported % 100 == 0:
                    frappe.db.commit()
                    print(f"Imported {imported} equipment registrations...")

            except Exception as e:
                errors.append({"row": i + 2, "job_asset_id": row.get('job_asset_id'), "error": str(e)})

    frappe.db.commit()

    print(f"\n=== Equipment Registration Import Complete ===")
    print(f"Imported: {imported}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {len(errors)}")

    if errors[:5]:
        print("\nFirst 5 errors:")
        for err in errors[:5]:
            print(f"  Row {err['row']}: {err['error']}")

    return {"imported": imported, "skipped": skipped, "errors": errors}


def import_warranty_registrations(csv_path="/workspace/development/warranty_registrations_rows.csv"):
    """Import warranty registrations from CSV"""
    valid_brands = get_valid_brands()
    imported = 0
    skipped = 0
    errors = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader):
            try:
                serial = row.get('serial')

                # Check if already exists by serial
                if serial and frappe.db.exists("Warranty Registration", {"serial": serial}):
                    skipped += 1
                    continue

                # Normalize brand
                brand = row.get('brand')
                if brand and brand not in valid_brands:
                    brand = None

                # Normalize processing status
                status_raw = row.get('processing_status', 'pending')
                processing_status = STATUS_MAP.get(status_raw, "Pending")

                # Parse dates
                install_date = row.get('install_date') or None
                purchase_date = row.get('purchase_date') or None
                processed_at = row.get('processed_at') or None

                if install_date:
                    try:
                        install_date = getdate(install_date)
                    except:
                        install_date = None

                if purchase_date:
                    try:
                        purchase_date = getdate(purchase_date)
                    except:
                        purchase_date = None

                doc = frappe.get_doc({
                    "doctype": "Warranty Registration",
                    "registering_as": normalize_registering_as(row.get('registering_as')),
                    "install_date": install_date,
                    "installation_type": row.get('installation_type'),
                    "purchase_date": purchase_date,
                    "dealer_id": row.get('dealer_id'),
                    "brand": brand,
                    "model": row.get('model'),
                    "serial": serial,
                    "model1": row.get('model1'),
                    "serial1": row.get('serial1'),
                    "model2": row.get('model2'),
                    "serial2": row.get('serial2'),
                    "model3": row.get('model3'),
                    "serial3": row.get('serial3'),
                    "model4": row.get('model4'),
                    "serial4": row.get('serial4'),
                    "model5": row.get('model5'),
                    "serial5": row.get('serial5'),
                    "model6": row.get('model6'),
                    "serial6": row.get('serial6'),
                    "model7": row.get('model7'),
                    "serial7": row.get('serial7'),
                    "model8": row.get('model8'),
                    "serial8": row.get('serial8'),
                    "model9": row.get('model9'),
                    "serial9": row.get('serial9'),
                    "owner_first_name": row.get('owner_first_name'),
                    "owner_last_name": row.get('owner_last_name'),
                    "owner_address": row.get('owner_street'),
                    "owner_city": row.get('owner_city'),
                    "owner_state": row.get('owner_state'),
                    "owner_zip": row.get('owner_zip_code'),
                    "owner_phone": row.get('owner_phone_number'),
                    "owner_email": row.get('owner_email_address'),
                    "contractor_name": row.get('contractor_name'),
                    "contractor_address": row.get('contractor_street'),
                    "contractor_city": row.get('contractor_city'),
                    "contractor_state": row.get('contractor_state'),
                    "contractor_zip": row.get('contractor_zipcode'),
                    "contractor_phone": row.get('contractor_phone_number'),
                    "contractor_email": row.get('contractor_email_address'),
                    "processing_status": processing_status,
                    "pdf_url": row.get('pdf_url'),
                    "error_message": row.get('error_message'),
                    "processed_at": processed_at,
                })
                doc.insert(ignore_permissions=True)
                imported += 1

            except Exception as e:
                errors.append({"row": i + 2, "serial": row.get('serial'), "error": str(e)})

    frappe.db.commit()

    print(f"\n=== Warranty Registration Import Complete ===")
    print(f"Imported: {imported}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {len(errors)}")

    if errors:
        print("\nErrors:")
        for err in errors:
            print(f"  Row {err['row']}: {err['error']}")

    return {"imported": imported, "skipped": skipped, "errors": errors}


def import_all():
    """Import all data from CSV files"""
    print("Starting CSV import...\n")

    print("=" * 50)
    print("Importing Equipment Registrations...")
    print("=" * 50)
    eq_result = import_equipment_registrations()

    print("\n" + "=" * 50)
    print("Importing Warranty Registrations...")
    print("=" * 50)
    wr_result = import_warranty_registrations()

    print("\n" + "=" * 50)
    print("FINAL SUMMARY")
    print("=" * 50)
    print(f"Equipment Registrations: {eq_result['imported']} imported, {eq_result['skipped']} skipped")
    print(f"Warranty Registrations: {wr_result['imported']} imported, {wr_result['skipped']} skipped")

    return {
        "equipment": eq_result,
        "warranty": wr_result
    }
