#!/usr/bin/env python3
"""
Bulk import script for equipment registrations from Supabase.
Run with: bench --site dev.localhost execute warranties.bulk_import.run_import
"""

import frappe

# Asset type mapping from Supabase integers to Frappe select options
ASSET_TYPE_MAP = {
    1: "HVAC",
    2: "Heat Pump",
    8: "Ventilation"
}

# Contact role mapping - normalize to valid DocType options
CONTACT_ROLE_MAP = {
    "Job Contact": "Job Contact",
    "Property Owner": "Property Owner",
    "Homeowner": "Property Owner",
    "Building Owner": "Property Owner",
    "Facility Manager": "Property Owner",
    "Property Manager": "Property Owner",
    "Billing Contact": "Property Owner",
}


def run_import():
    """Import all equipment registrations from Supabase via direct query"""
    # This would normally fetch from Supabase, but we'll use sample data for now
    print("Starting bulk import...")

    # Sample batch from Supabase (first 5 records)
    sample_data = [
        {"job_asset_id":12345,"job_number":1001,"job_address":"123 Main Street","city":"Toronto","province":"ON","postal_code":"M5H 2N2","brand":"Carrier","indoor_model":"ABC123","indoor_serial":"SN123456","outdoor_model":"XYZ789","outdoor_serial":"SN789012","install_date":"2025-01-15","asset_type":1,"customer_first_name":"John","customer_last_name":"Doe","customer_email":"john.doe@example.com","customer_phone":"416-555-0100","contact_role":"Homeowner"},
        {"job_asset_id":12346,"job_number":1002,"job_address":"456 Oak Avenue","city":"Vancouver","province":"BC","postal_code":"V6B 2W9","brand":"Lennox","indoor_model":"DEF456","indoor_serial":"SN234567","outdoor_model":"UVW890","outdoor_serial":"SN890123","install_date":"2025-01-16","asset_type":1,"customer_first_name":"Jane","customer_last_name":"Smith","customer_email":"jane.smith@example.com","customer_phone":"604-555-0200","contact_role":"Property Manager"},
        {"job_asset_id":12347,"job_number":1003,"job_address":"789 Elm Street","city":"Calgary","province":"AB","postal_code":"T2P 5C5","brand":"Trane","indoor_model":"GHI789","indoor_serial":"SN345678","outdoor_model":"RST901","outdoor_serial":"SN901234","install_date":"2025-01-17","asset_type":2,"customer_first_name":"Bob","customer_last_name":"Johnson","customer_email":"bob.johnson@example.com","customer_phone":"403-555-0300","contact_role":"Building Owner"},
        {"job_asset_id":12348,"job_number":1004,"job_address":"321 Maple Drive","city":"Montreal","province":"QC","postal_code":"H3B 4W8","brand":"York","indoor_model":"JKL012","indoor_serial":"SN456789","outdoor_model":"OPQ012","outdoor_serial":"SN012345","install_date":"2025-01-18","asset_type":1,"customer_first_name":"Alice","customer_last_name":"Williams","customer_email":"alice.williams@example.com","customer_phone":"514-555-0400","contact_role":"Facility Manager"},
        {"job_asset_id":12349,"job_number":1005,"job_address":"654 Pine Road","city":"Ottawa","province":"ON","postal_code":"K1P 5M4","brand":"Goodman","indoor_model":"MNO345","indoor_serial":"SN567890","outdoor_model":"LMN123","outdoor_serial":"SN123456","install_date":"2025-01-19","asset_type":2,"customer_first_name":"Charlie","customer_last_name":"Brown","customer_email":"charlie.brown@example.com","customer_phone":"613-555-0500","contact_role":"Homeowner"},
    ]

    created, skipped, errors = import_batch(sample_data)
    print(f"Import complete: {created} created, {skipped} skipped, {len(errors)} errors")
    if errors:
        for err in errors:
            print(f"  Error: {err}")
    return {"created": created, "skipped": skipped, "errors": errors}


def import_batch(data_batch):
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

            # Map contact_role to valid options
            contact_role = item.get("contact_role", "")
            if contact_role:
                contact_role = CONTACT_ROLE_MAP.get(contact_role, "")

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
                "contact_role": contact_role,
            })
            doc.insert(ignore_permissions=True)
            created += 1
        except Exception as e:
            errors.append({"job_asset_id": item.get("job_asset_id"), "error": str(e)})

    frappe.db.commit()
    return created, skipped, errors
