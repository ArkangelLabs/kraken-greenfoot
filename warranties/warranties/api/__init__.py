# Copyright (c) 2024, Kraken and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import now_datetime
import requests
import json

# Greenfoot Energy API Configuration
GREENFOOT_API_URL = frappe.conf.get("greenfoot_api_url", "http://localhost:8000")


@frappe.whitelist()
def create_equipment_registration(data: dict) -> dict:
    """
    Create an equipment registration record.
    Called by AWS Step Function to create equipment registrations.

    Args:
        data: Dictionary containing equipment registration fields

    Returns:
        Dictionary with created document name and status
    """
    doc = frappe.get_doc({
        "doctype": "Equipment Registration",
        **data
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "success": True,
        "name": doc.name,
        "message": _("Equipment Registration created successfully")
    }


@frappe.whitelist()
def create_warranty_registration(data: dict) -> dict:
    """
    Create a warranty registration record and queue it for processing.
    Called by AWS Step Function to queue warranty registrations.

    Args:
        data: Dictionary containing warranty registration fields

    Returns:
        Dictionary with created document name and status
    """
    # Set default status if not provided
    if "processing_status" not in data:
        data["processing_status"] = "Pending"

    doc = frappe.get_doc({
        "doctype": "Warranty Registration",
        **data
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "success": True,
        "name": doc.name,
        "message": _("Warranty Registration queued for processing")
    }


@frappe.whitelist()
def update_warranty_status(
    name: str,
    status: str,
    pdf_url: str = None,
    error: str = None
) -> dict:
    """
    Update warranty registration processing status.
    Called by AWS Step Function on processing completion.

    Args:
        name: Warranty Registration document name
        status: New status (Processing, Completed, Failed)
        pdf_url: S3 URL of warranty certificate PDF (for Completed status)
        error: Error message (for Failed status)

    Returns:
        Dictionary with update status
    """
    if not frappe.db.exists("Warranty Registration", name):
        frappe.throw(_("Warranty Registration {0} not found").format(name))

    doc = frappe.get_doc("Warranty Registration", name)
    doc.processing_status = status

    if pdf_url:
        doc.pdf_url = pdf_url

    if error:
        doc.error_message = error

    if status in ["Completed", "Failed"]:
        doc.processed_at = now_datetime()

    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "success": True,
        "name": doc.name,
        "status": doc.processing_status,
        "message": _("Warranty Registration status updated to {0}").format(status)
    }


@frappe.whitelist()
def get_manufacturer_config(brand: str) -> dict:
    """
    Get manufacturer registration configuration for automation.

    Args:
        brand: Manufacturer brand name

    Returns:
        Dictionary with manufacturer configuration including registration URL,
        required fields, and markdown guide
    """
    if not frappe.db.exists("HVAC Manufacturer", brand):
        return {
            "success": False,
            "message": _("Manufacturer {0} not found").format(brand)
        }

    doc = frappe.get_doc("HVAC Manufacturer", brand)

    fields_needed = []
    for field in doc.fields_needed:
        fields_needed.append({
            "field_name": field.field_name,
            "field_type": field.field_type,
            "required": field.required
        })

    return {
        "success": True,
        "brand": doc.brand,
        "type": doc.type,
        "registration_url": doc.registration_url,
        "fields_needed": fields_needed,
        "markdown_guide": doc.markdown_guide
    }


@frappe.whitelist()
def bulk_import_equipment(registrations: list) -> dict:
    """
    Bulk import equipment registrations from CSV/JSON data.

    Args:
        registrations: List of dictionaries containing equipment registration data

    Returns:
        Dictionary with import results
    """
    if not isinstance(registrations, list):
        frappe.throw(_("registrations must be a list"))

    created = []
    errors = []

    for idx, data in enumerate(registrations):
        try:
            doc = frappe.get_doc({
                "doctype": "Equipment Registration",
                **data
            })
            doc.insert(ignore_permissions=True)
            created.append(doc.name)
        except Exception as e:
            errors.append({
                "index": idx,
                "data": data,
                "error": str(e)
            })

    frappe.db.commit()

    return {
        "success": len(errors) == 0,
        "created_count": len(created),
        "error_count": len(errors),
        "created": created,
        "errors": errors
    }


@frappe.whitelist()
def get_pending_warranties() -> list:
    """
    Get all pending warranty registrations for processing.

    Returns:
        List of pending warranty registration documents
    """
    warranties = frappe.get_all(
        "Warranty Registration",
        filters={"processing_status": "Pending"},
        fields=["name", "brand", "model", "serial", "owner_first_name",
                "owner_last_name", "owner_email_address", "install_date"]
    )
    return warranties


@frappe.whitelist()
def log_agent_activity(
    task: str,
    status: str,
    message: str = None,
    error_message: str = None,
    confirmation_number: str = None,
    registration_url: str = None,
    warranty_registration: str = None,
    brand: str = None,
    execution_id: str = None,
    video_url: str = None,
    screenshot_url: str = None,
    pdf_url: str = None,
    proofs_folder: str = None,
    duration_seconds: float = None
) -> dict:
    """
    Log Nova Act agent processing activity with proof links.

    Args:
        task: Description of the task
        status: Status (In Progress, Success, Failed)
        message: General status message
        error_message: Error details if failed
        confirmation_number: Warranty confirmation number from portal
        registration_url: URL to warranty confirmation page
        warranty_registration: Link to Warranty Registration document
        brand: HVAC Manufacturer brand name
        execution_id: Step Functions execution ID
        video_url: S3 URL to video recording
        screenshot_url: S3 URL to screenshot
        pdf_url: S3 URL to warranty certificate PDF
        proofs_folder: S3 folder containing all proofs
        duration_seconds: Duration of automation run

    Returns:
        Dictionary with created log name
    """
    doc_data = {
        "doctype": "Agent Log",
        "task": task,
        "status": status,
        "timestamp": now_datetime()
    }

    # Add optional fields if provided
    if message:
        doc_data["message"] = message
    if error_message:
        doc_data["error_message"] = error_message
    if confirmation_number:
        doc_data["confirmation_number"] = confirmation_number
    if registration_url:
        doc_data["registration_url"] = registration_url
    if warranty_registration:
        doc_data["warranty_registration"] = warranty_registration
    if brand:
        doc_data["brand"] = brand
    if execution_id:
        doc_data["execution_id"] = execution_id
    if video_url:
        doc_data["video_url"] = video_url
    if screenshot_url:
        doc_data["screenshot_url"] = screenshot_url
    if pdf_url:
        doc_data["pdf_url"] = pdf_url
    if proofs_folder:
        doc_data["proofs_folder"] = proofs_folder
    if duration_seconds is not None:
        doc_data["duration_seconds"] = duration_seconds

    doc = frappe.get_doc(doc_data)
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "success": True,
        "name": doc.name
    }


@frappe.whitelist()
def trigger_demo_dry_run(brand: str) -> dict:
    """
    Trigger a demo dry run via Step Function.

    Args:
        brand: HVAC Manufacturer brand name

    Returns:
        Dictionary with execution ARN and status
    """
    import boto3
    import uuid

    # Validate brand exists
    if not frappe.db.exists("HVAC Manufacturer", brand):
        frappe.throw(_("HVAC Manufacturer '{0}' not found").format(brand))

    # Get AWS credentials from site_config.json
    aws_access_key = frappe.conf.get("aws_access_key_id")
    aws_secret_key = frappe.conf.get("aws_secret_access_key")
    aws_region = frappe.conf.get("aws_region", "us-east-1")

    if not aws_access_key or not aws_secret_key:
        frappe.throw(_("AWS credentials not configured in site_config.json"))

    # Map HVAC Manufacturer names to Step Function brand keys
    brand_map = {
        "GE (HVAC Partner Program)": "ge",
        "Samsung HVAC (commercial & new build)": "samsung",
        "Samsung HVAC (retrofit)": "samsung",
        "Napoleon (HVAC)": "napoleon",
        "Mitsubishi (Mesca)": "mitsubishi",
        "Daikin": "daikin",
        "ADP Coils (BC)": "adp_coils",
        "American Standard / Ameristar (central)": "american_standard",
        "Arcoaire (ICP)": "arcoaire",
        "Tempstar (ICP)": "tempstar",
        "KeepRite (ICP)": "keeprite",
        "Fantech": "fantech",
    }

    lambda_brand = brand_map.get(brand)
    if not lambda_brand:
        frappe.throw(_("No demo automation available for brand: {0}").format(brand))

    # Build CSV content (header + demo row)
    csv_header = "brand,outdoor_model,outdoor_serial,customer_first_name,customer_last_name,customer_email,customer_phone,job_address,city,province,postal_code,install_date"
    csv_row = f"{lambda_brand},DEMO-MODEL,DEMO-{lambda_brand.upper()}-001,Demo,Customer,demo@greenfoot-test.com,5551234567,123 Demo Street,Moncton,NB,E1A 1A1,2025-01-15"
    csv_content = f"{csv_header}\n{csv_row}"

    try:
        # Start Step Function execution
        sfn_client = boto3.client(
            "stepfunctions",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )

        execution_name = f"demo-{lambda_brand}-{uuid.uuid4().hex[:8]}"

        response = sfn_client.start_execution(
            stateMachineArn="arn:aws:states:us-east-1:835156585962:stateMachine:nova-act-warranty-processor",
            name=execution_name,
            input=json.dumps({
                "csv_content": csv_content,
                "dry_run": True,
                "source": "frappe-demo"
            })
        )

        return {
            "success": True,
            "execution_arn": response["executionArn"],
            "execution_name": execution_name,
            "message": _("Demo started. Check Agent Logs for results.")
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Demo Dry Run Error - {brand}")
        frappe.throw(_("Demo run failed: {0}").format(str(e)))


@frappe.whitelist()
def get_demo_supported_brands() -> dict:
    """
    Get list of HVAC Manufacturer names that support demo dry runs.

    Returns:
        Dictionary with list of supported brand names
    """
    # Brands with Nova Act automation support
    supported = [
        "GE (HVAC Partner Program)",
        "Samsung HVAC (commercial & new build)",
        "Samsung HVAC (retrofit)",
        "Napoleon (HVAC)",
        "Mitsubishi (Mesca)",
        "Daikin",
        "ADP Coils (BC)",
        "American Standard / Ameristar (central)",
        "Arcoaire (ICP)",
        "Tempstar (ICP)",
        "KeepRite (ICP)",
    ]
    return {"brands": supported}


@frappe.whitelist()
def get_s3_download_url(s3_uri: str, expires_in: int = 3600) -> dict:
    """
    Generate presigned URL for S3 object download.

    Reads AWS credentials from site_config.json via frappe.conf.

    Args:
        s3_uri: S3 URI (s3://bucket/key)
        expires_in: URL expiry in seconds (default 1 hour)

    Returns:
        dict with presigned URL
    """
    import boto3

    if not s3_uri or not s3_uri.startswith("s3://"):
        frappe.throw(_("Invalid S3 URI"))

    # Get AWS config from site_config.json (set via bench set-config)
    aws_access_key = frappe.conf.get("aws_access_key_id")
    aws_secret_key = frappe.conf.get("aws_secret_access_key")
    aws_region = frappe.conf.get("aws_region", "us-east-1")

    if not aws_access_key or not aws_secret_key:
        frappe.throw(_("AWS credentials not configured in site_config.json"))

    # Parse s3://bucket/key
    path = s3_uri.replace("s3://", "")
    bucket, key = path.split("/", 1)

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region
    )

    url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires_in
    )

    return {"url": url}


@frappe.whitelist()
def get_brand_credentials(brand: str) -> dict:
    """
    Get portal credentials for a brand (for Nova Act automation).
    
    Called by Lambda/Step Functions to retrieve login credentials.
    Requires API key authentication.
    
    Args:
        brand: Brand key (ge, mitsubishi, lg, fujitsu)
        
    Returns:
        dict with username and password if configured
    """
    from frappe.utils.password import get_decrypted_password
    
    brand_lower = brand.lower().replace(" ", "_").replace("-", "_")
    
    # Map common brand names to field prefixes
    brand_map = {
        "ge": "ge",
        "ge_hvac": "ge",
        "mitsubishi": "mitsubishi",
        "mesca": "mitsubishi",
        "lg": "lg",
        "fujitsu": "fujitsu",
    }
    
    field_prefix = brand_map.get(brand_lower, brand_lower)
    
    try:
        doc = frappe.get_single("Brand Credentials")
        username = getattr(doc, f"{field_prefix}_username", None)
        
        if not username:
            return {
                "success": False,
                "error": f"No credentials configured for {brand}"
            }
        
        password = get_decrypted_password(
            "Brand Credentials",
            "Brand Credentials",
            f"{field_prefix}_password"
        )
        
        return {
            "success": True,
            "brand": brand,
            "username": username,
            "password": password or ""
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
