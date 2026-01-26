import frappe

def execute():
    # Delete client script
    if frappe.db.exists("Client Script", "Agent Log - Render Details"):
        frappe.delete_doc("Client Script", "Agent Log - Render Details", force=True)
        print("Deleted Client Script")
    
    frappe.db.commit()
