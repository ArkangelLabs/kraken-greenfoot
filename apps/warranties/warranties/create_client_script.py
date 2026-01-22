import frappe

def execute():
    script = '''
frappe.ui.form.on("Agent Log", {
    refresh: function(frm) {
        render_details(frm);
    }
});

function render_details(frm) {
    let d = frm.doc.details;
    if (!d) { frm.set_df_property("details_html", "options", "<p>No details</p>"); return; }
    if (typeof d === "string") { try { d = JSON.parse(d); } catch(e) { return; } }
    
    let html = "<div style='display:grid;grid-template-columns:1fr 1fr;gap:20px;'>" +
        "<div>" +
        "<p><b>Brand:</b> " + (d.brand || "-") + "</p>" +
        "<p><b>Session:</b> " + (d.session_id || "-").substring(0,8) + "</p>" +
        "<p><b>Duration:</b> " + (d.total_time_worked_s || 0).toFixed(1) + "s</p>" +
        "<p><b>Actions:</b> " + (d.act_count || 0) + "</p>" +
        "</div><div>";
    
    if (d.video_path) {
        html += "<p><a href='" + d.video_path + "' target='_blank'>Watch Video</a></p>";
    }
    
    let reps = d.html_reports || [];
    if (reps.length > 0) {
        html += "<p><b>Reports:</b></p><ul>";
        reps.slice(0,5).forEach(function(r) {
            html += "<li><a href='" + r + "' target='_blank'>" + r.split("/").pop().substring(0,30) + "</a></li>";
        });
        if (reps.length > 5) { html += "<li>+" + (reps.length - 5) + " more</li>"; }
        html += "</ul>";
    }
    html += "</div></div>";
    frm.set_df_property("details_html", "options", html);
}
'''
    
    name = "Agent Log - Render Details"
    
    if frappe.db.exists("Client Script", name):
        doc = frappe.get_doc("Client Script", name)
        doc.script = script
        doc.save(ignore_permissions=True)
        print("Updated Client Script")
    else:
        doc = frappe.get_doc({
            "doctype": "Client Script",
            "name": name,
            "dt": "Agent Log",
            "view": "Form",
            "enabled": 1,
            "script": script
        })
        doc.insert(ignore_permissions=True)
        print("Created Client Script")
    
    frappe.db.commit()
