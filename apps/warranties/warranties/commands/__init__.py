import click
import frappe
from frappe.commands import pass_context


@click.command("import-extraction-logs")
@pass_context
def import_extraction_logs(context):
    """Import agent extraction logs from files directory into Agent Log doctype."""
    import os
    import json
    from pathlib import Path
    
    site = context.sites[0] if context.sites else "greenfoot-energy.mythril.cloud"
    
    frappe.init(site=site)
    frappe.connect()
    
    files_path = Path(frappe.get_site_path("public", "files", "agent_extraction_logs"))
    
    if not files_path.exists():
        click.echo(f"Directory not found: {files_path}")
        return
    
    sessions_path = files_path / "sessions"
    videos_path = files_path / "videos"
    html_path = files_path / "html_reports"
    
    if not sessions_path.exists():
        click.echo(f"Sessions directory not found: {sessions_path}")
        return
    
    imported = 0
    errors = 0
    
    # Iterate through brand folders in sessions
    for brand_dir in sessions_path.iterdir():
        if not brand_dir.is_dir():
            continue
            
        brand = brand_dir.name
        click.echo(f"Processing brand: {brand}")
        
        # Find session JSON files
        for session_file in brand_dir.glob("*_session.json"):
            try:
                with open(session_file) as f:
                    session_data = json.load(f)
                
                session_id = session_data.get("session_id", "")[:8]
                
                # Find associated video
                video_path = ""
                if videos_path.exists():
                    brand_videos = videos_path / brand
                    if brand_videos.exists():
                        for video in brand_videos.glob(f"*{session_id}*.webm"):
                            video_path = f"/files/agent_extraction_logs/videos/{brand}/{video.name}"
                            break
                
                # Find associated HTML reports
                html_reports = []
                if html_path.exists():
                    brand_html = html_path / brand
                    if brand_html.exists():
                        for html_file in brand_html.glob(f"*{session_id}*.html"):
                            html_reports.append(f"/files/agent_extraction_logs/html_reports/{brand}/{html_file.name}")
                
                # Create Agent Log entry with JSON string
                details = {
                    "session_id": session_data.get("session_id", ""),
                    "brand": brand,
                    "total_time_worked_s": session_data.get("total_time_worked_s", 0),
                    "act_count": session_data.get("act_count", 0),
                    "video_path": video_path,
                    "html_reports": html_reports
                }
                
                doc = frappe.get_doc({
                    "doctype": "Agent Log",
                    "task": f"Agent Extraction - {brand}",
                    "status": "Success",
                    "details": json.dumps(details)
                })
                doc.insert(ignore_permissions=True)
                imported += 1
                click.echo(f"  Imported: {session_file.name}")
                
            except Exception as e:
                errors += 1
                click.echo(f"  Error processing {session_file.name}: {e}")
    
    frappe.db.commit()
    frappe.destroy()
    
    click.echo(f"\nImport complete: {imported} sessions imported, {errors} errors")


commands = [import_extraction_logs]
