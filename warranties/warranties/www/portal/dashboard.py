import frappe
from frappe import _

no_cache = 1


def get_context(context):
    """Portal dashboard for dealers/contractors"""
    # Authentication
    if frappe.session.user == "Guest":
        frappe.throw(_("Please log in to access the dashboard"), frappe.PermissionError)

    # Authorization - require Kraken End User role
    user_roles = frappe.get_roles()
    if "Kraken End User" not in user_roles and "Administrator" not in user_roles:
        frappe.throw(_("You don't have permission to access this page"), frappe.PermissionError)

    user = frappe.get_doc("User", frappe.session.user)
    context.title = "Warranties Dashboard"
    context.user_name = user.full_name

    # Number card data
    context.total_equipment = frappe.db.count("Equipment Registration")
    context.pending_warranties = frappe.db.count(
        "Warranty Registration", {"processing_status": "Pending"}
    )
    context.completed_warranties = frappe.db.count(
        "Warranty Registration", {"processing_status": "Completed"}
    )
    context.failed_warranties = frappe.db.count(
        "Warranty Registration", {"processing_status": "Failed"}
    )

    return context


@frappe.whitelist()
def get_monthly_installations():
    """Line chart: Monthly installations over last year"""
    data = frappe.db.sql(
        """
        SELECT DATE_FORMAT(install_date, '%%Y-%%m') as month,
               COUNT(*) as count
        FROM `tabEquipment Registration`
        WHERE install_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        GROUP BY DATE_FORMAT(install_date, '%%Y-%%m')
        ORDER BY month
    """,
        as_dict=True,
    )

    return {
        "labels": [d["month"] for d in data] if data else [],
        "datasets": [{"name": "Installations", "values": [d["count"] for d in data]}]
        if data
        else [{"name": "Installations", "values": []}],
    }


@frappe.whitelist()
def get_registrations_by_brand():
    """Pie chart: Equipment by brand"""
    data = frappe.db.sql(
        """
        SELECT brand, COUNT(*) as count
        FROM `tabEquipment Registration`
        GROUP BY brand
        ORDER BY count DESC
        LIMIT 10
    """,
        as_dict=True,
    )

    return {
        "labels": [d["brand"] or "Unknown" for d in data] if data else [],
        "datasets": [{"values": [d["count"] for d in data]}] if data else [{"values": []}],
    }


@frappe.whitelist()
def get_registrations_by_province():
    """Bar chart: Equipment by province"""
    data = frappe.db.sql(
        """
        SELECT province, COUNT(*) as count
        FROM `tabEquipment Registration`
        GROUP BY province
        ORDER BY count DESC
        LIMIT 15
    """,
        as_dict=True,
    )

    return {
        "labels": [d["province"] or "Unknown" for d in data] if data else [],
        "datasets": [{"name": "Registrations", "values": [d["count"] for d in data]}]
        if data
        else [{"name": "Registrations", "values": []}],
    }


@frappe.whitelist()
def get_warranty_status():
    """Donut chart: Warranty processing status"""
    data = frappe.db.sql(
        """
        SELECT processing_status, COUNT(*) as count
        FROM `tabWarranty Registration`
        GROUP BY processing_status
    """,
        as_dict=True,
    )

    return {
        "labels": [d["processing_status"] or "Unknown" for d in data] if data else [],
        "datasets": [{"values": [d["count"] for d in data]}] if data else [{"values": []}],
    }
