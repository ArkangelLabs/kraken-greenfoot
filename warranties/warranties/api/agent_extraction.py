# Copyright (c) 2024, Kraken and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _
from frappe.utils import now_datetime


@frappe.whitelist()
def import_session(session_data: dict) -> dict:
    """
    Import an extraction session into Agent Log.
    
    Args:
        session_data: Dictionary containing session metadata
        
    Returns:
        Dictionary with created document name
    """
    brand = session_data.get("brand", "unknown")
    
    doc = frappe.get_doc({
        "doctype": "Agent Log",
        "task": f"Agent Extraction - {brand}",
        "status": "Success",
        "timestamp": now_datetime(),
        "details": session_data
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    
    return {
        "success": True,
        "name": doc.name
    }


@frappe.whitelist()
def get_extraction_sessions(brand: str = None, status: str = None, limit: int = 50) -> list:
    """
    Query extraction sessions with parsed JSON details.
    
    Args:
        brand: Filter by brand name
        status: Filter by status
        limit: Max results to return
        
    Returns:
        List of extraction sessions
    """
    filters = {"task": ["like", "Agent Extraction%"]}
    
    if status:
        filters["status"] = status
    
    logs = frappe.get_all(
        "Agent Log",
        filters=filters,
        fields=["name", "task", "status", "timestamp", "details"],
        order_by="timestamp desc",
        limit=limit
    )
    
    sessions = []
    for log in logs:
        details = log.get("details") or {}
        if isinstance(details, str):
            try:
                details = json.loads(details)
            except:
                details = {}
        
        log_brand = details.get("brand", "")
        
        # Apply brand filter on parsed details
        if brand and log_brand != brand:
            continue
            
        sessions.append({
            "name": log.name,
            "task": log.task,
            "status": log.status,
            "timestamp": log.timestamp,
            "brand": log_brand,
            "session_id": details.get("session_id", ""),
            "total_time_s": details.get("total_time_worked_s", 0),
            "act_count": details.get("act_count", 0),
            "video_path": details.get("video_path", ""),
            "html_reports": details.get("html_reports", [])
        })
    
    return sessions


@frappe.whitelist()
def get_extraction_metrics() -> dict:
    """
    Get aggregate stats for extraction sessions.
    
    Returns:
        Dictionary with total, success rate, avg time, by brand
    """
    logs = frappe.get_all(
        "Agent Log",
        filters={"task": ["like", "Agent Extraction%"]},
        fields=["name", "status", "details"]
    )
    
    total = len(logs)
    success_count = 0
    total_time = 0
    by_brand = {}
    
    for log in logs:
        if log.status == "Success":
            success_count += 1
            
        details = log.get("details") or {}
        if isinstance(details, str):
            try:
                details = json.loads(details)
            except:
                details = {}
        
        brand = details.get("brand", "unknown")
        time_worked = details.get("total_time_worked_s", 0)
        total_time += time_worked
        
        if brand not in by_brand:
            by_brand[brand] = {"count": 0, "success": 0, "total_time": 0}
        by_brand[brand]["count"] += 1
        by_brand[brand]["total_time"] += time_worked
        if log.status == "Success":
            by_brand[brand]["success"] += 1
    
    return {
        "total_sessions": total,
        "success_count": success_count,
        "success_rate": round((success_count / total * 100) if total > 0 else 0, 1),
        "avg_time_s": round(total_time / total if total > 0 else 0, 1),
        "total_time_s": round(total_time, 1),
        "by_brand": by_brand
    }


@frappe.whitelist()
def get_success_rate_card() -> dict:
    """Number card method for success rate."""
    metrics = get_extraction_metrics()
    return {
        "value": metrics["success_rate"],
        "fieldtype": "Percent"
    }


@frappe.whitelist()
def get_avg_time_card() -> dict:
    """Number card method for average time."""
    metrics = get_extraction_metrics()
    return {
        "value": metrics["avg_time_s"],
        "fieldtype": "Float"
    }
