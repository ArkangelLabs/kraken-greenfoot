import frappe

def execute():
    """Migrate existing Agent Log records to populate display fields."""
    logs = frappe.get_all(
        "Agent Log",
        filters={"task": ["like", "Agent Extraction%"]},
        pluck="name"
    )
    
    print(f"Found {len(logs)} Agent Extraction logs to migrate")
    
    for name in logs:
        doc = frappe.get_doc("Agent Log", name)
        doc.save(ignore_permissions=True)
        print(f"Migrated: {name}")
    
    frappe.db.commit()
    print("Migration complete")
