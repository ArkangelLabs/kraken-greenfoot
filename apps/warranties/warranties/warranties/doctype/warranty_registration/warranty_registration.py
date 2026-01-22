# Copyright (c) 2024, Kraken and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime
import json
import uuid


class WarrantyRegistration(Document):
    def before_save(self):
        # Set processed_at when status changes to Completed or Failed
        if self.has_value_changed("processing_status"):
            if self.processing_status in ["Completed", "Failed"]:
                self.processed_at = now_datetime()


@frappe.whitelist()
def trigger_dry_run(brand, registration_name=None):
    """Trigger a dry run workflow for a single registration.

    Args:
        brand: Brand name (e.g., 'Fantech')
        registration_name: Optional specific registration to test

    Returns:
        dict with success status and execution_arn
    """
    return trigger_dry_run_batch(brand, limit=1)


@frappe.whitelist()
def trigger_dry_run_batch(brand, limit=5):
    """Trigger dry run for recent registrations of a brand via Step Functions.

    Args:
        brand: Brand name (e.g., 'Fantech')
        limit: Number of records to process (default 5)

    Returns:
        dict with success status, execution_arn, and count
    """
    try:
        import boto3
        from botocore.exceptions import ClientError

        # Get AWS config from site config
        aws_region = frappe.conf.get("aws_region", "us-east-1")
        aws_access_key = frappe.conf.get("aws_access_key_id")
        aws_secret_key = frappe.conf.get("aws_secret_access_key")
        step_function_arn = frappe.conf.get(
            "dry_run_step_function_arn",
            "arn:aws:states:us-east-1:835156585962:stateMachine:greenfoot-dry-run-processor"
        )

        # Create Step Functions client with explicit credentials
        if aws_access_key and aws_secret_key:
            sfn_client = boto3.client(
                "stepfunctions",
                region_name=aws_region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
        else:
            sfn_client = boto3.client("stepfunctions", region_name=aws_region)

        # Generate unique execution name
        execution_name = f"dryrun-{brand.lower().replace(' ', '-')}-{uuid.uuid4().hex[:8]}"

        # Prepare input for Step Function
        sfn_input = {
            "brand": brand,
            "limit": int(limit),
            "dry_run": True
        }

        # Start Step Function execution
        response = sfn_client.start_execution(
            stateMachineArn=step_function_arn,
            name=execution_name,
            input=json.dumps(sfn_input)
        )

        execution_arn = response.get("executionArn", "")

        # Log the trigger
        frappe.log_error(
            title="Dry Run Triggered via Step Functions",
            message=f"Brand: {brand}\nLimit: {limit}\nExecution ARN: {execution_arn}"
        )

        return {
            "success": True,
            "execution_arn": execution_arn,
            "execution_id": execution_name,
            "count": limit,
            "message": f"Dry run triggered for {limit} latest {brand} registrations"
        }

    except ClientError as e:
        error_msg = str(e)
        frappe.log_error(title="Dry Run Step Functions Error", message=error_msg)
        return {"success": False, "error": error_msg}

    except ImportError:
        return {
            "success": False,
            "error": "boto3 not installed. Run: pip install boto3"
        }

    except Exception as e:
        frappe.log_error(title="Dry Run Error", message=str(e))
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_dry_run_status(execution_arn):
    """Get the status of a dry run execution.

    Args:
        execution_arn: Step Functions execution ARN

    Returns:
        dict with execution status and results
    """
    try:
        import boto3

        aws_region = frappe.conf.get("aws_region", "us-east-1")
        aws_access_key = frappe.conf.get("aws_access_key_id")
        aws_secret_key = frappe.conf.get("aws_secret_access_key")

        if aws_access_key and aws_secret_key:
            sfn_client = boto3.client(
                "stepfunctions",
                region_name=aws_region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
        else:
            sfn_client = boto3.client("stepfunctions", region_name=aws_region)

        response = sfn_client.describe_execution(executionArn=execution_arn)

        result = {
            "success": True,
            "status": response.get("status"),
            "start_date": str(response.get("startDate", "")),
            "stop_date": str(response.get("stopDate", "")) if response.get("stopDate") else None,
        }

        # If completed, include output
        if response.get("status") == "SUCCEEDED" and response.get("output"):
            result["output"] = json.loads(response["output"])

        # If failed, include error
        if response.get("status") == "FAILED":
            result["error"] = response.get("error", "Unknown error")
            result["cause"] = response.get("cause", "")

        return result

    except Exception as e:
        return {"success": False, "error": str(e)}
