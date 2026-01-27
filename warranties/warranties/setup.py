import frappe


def after_install():
	"""Run after app installation."""
	create_warranties_manager_role()
	frappe.db.commit()


def create_warranties_manager_role():
	"""Create Warranties Manager role if it doesn't exist."""
	role_name = "Warranties Manager"

	if frappe.db.exists("Role", role_name):
		return

	frappe.get_doc({
		"doctype": "Role",
		"role_name": role_name,
		"desk_access": 1,
		"is_custom": 1,
		"home_page": "/app/warranties",
	}).insert(ignore_permissions=True)

	frappe.logger().info(f"Created Role: {role_name}")
