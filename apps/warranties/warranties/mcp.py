import json
import frappe
import frappe_mcp

mcp = frappe_mcp.MCP("warranties")


@mcp.tool()
def get_warranty_registrations(brand: str = None, status: str = None, limit: int = 10):
    """Get warranty registrations from ERPNext
    
    Args:
        brand: Filter by brand/manufacturer name (optional)
        status: Filter by processing_status (Pending, Processing, Completed, Failed)
        limit: Maximum number of records to return (default 10)
    """
    filters = {}
    if brand:
        filters["brand"] = brand
    if status:
        filters["processing_status"] = status
    
    registrations = frappe.get_all(
        "Warranty Registration",
        filters=filters,
        fields=["name", "brand", "serial", "model", "owner_first_name", "owner_last_name",
                "install_date", "processing_status", "creation"],
        limit_page_length=limit,
        order_by="creation desc"
    )
    return registrations


@mcp.tool()
def get_warranty_details(registration_name: str):
    """Get full details of a specific warranty registration
    
    Args:
        registration_name: The document name/ID of the warranty registration
    """
    doc = frappe.get_doc("Warranty Registration", registration_name)
    return doc.as_dict()


@mcp.tool()
def get_manufacturers():
    """Get list of all HVAC manufacturers/brands in the system"""
    manufacturers = frappe.get_all(
        "HVAC Manufacturer",
        fields=["name", "brand", "type", "registration_url"],
        order_by="brand asc"
    )
    return manufacturers


@mcp.tool()
def get_registration_stats():
    """Get summary statistics of warranty registrations by status and brand"""
    # Get counts by status
    status_counts = frappe.db.sql("""
        SELECT processing_status, COUNT(*) as count 
        FROM `tabWarranty Registration` 
        GROUP BY processing_status
    """, as_dict=True) or []
    
    # Get counts by brand
    brand_counts = frappe.db.sql("""
        SELECT brand, COUNT(*) as count 
        FROM `tabWarranty Registration` 
        GROUP BY brand 
        ORDER BY count DESC
        LIMIT 10
    """, as_dict=True) or []
    
    total = sum(s.get("count", 0) for s in status_counts)
    
    return json.dumps({
        "by_status": status_counts,
        "by_brand": brand_counts,
        "total": total
    }, default=str)


@mcp.tool()
def search_registrations(query: str, limit: int = 20):
    """Search warranty registrations by serial number, owner name, or brand
    
    Args:
        query: Search term to match against serial, owner names, or brand
        limit: Maximum results to return (default 20)
    """
    results = frappe.db.sql("""
        SELECT name, brand, serial, model, owner_first_name, owner_last_name,
               processing_status, creation
        FROM `tabWarranty Registration`
        WHERE serial LIKE %(query)s
           OR owner_first_name LIKE %(query)s
           OR owner_last_name LIKE %(query)s
           OR brand LIKE %(query)s
        ORDER BY creation DESC
        LIMIT %(limit)s
    """, {"query": f"%{query}%", "limit": limit}, as_dict=True) or []
    return results


@mcp.tool()
def get_agent_logs(limit: int = 20, brand: str = None):
    """Get recent agent/automation logs
    
    Args:
        limit: Maximum number of logs to return (default 20)
        brand: Filter by brand (optional)
    """
    filters = {}
    if brand:
        filters["brand"] = brand
    
    logs = frappe.get_all(
        "Agent Log",
        filters=filters,
        fields=["name", "brand", "status", "message", "creation", "execution_id", 
                "is_demo_run", "pdf_url", "screenshot_url"],
        limit_page_length=limit,
        order_by="creation desc"
    )
    return logs


@mcp.register(allow_guest=True)
def handle_mcp():
    """MCP endpoint handler"""
    import warranties.mcp  # ensure tools are loaded
