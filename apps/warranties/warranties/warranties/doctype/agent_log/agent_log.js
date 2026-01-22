// Copyright (c) 2024, Kraken and contributors
// For license information, please see license.txt

// Helper function to open S3 URLs via presigned URL API
function open_s3_url(s3_uri) {
    if (!s3_uri) return;

    // If it's an s3:// URI, get presigned URL first
    if (s3_uri.startsWith('s3://')) {
        frappe.call({
            method: 'warranties.api.get_s3_download_url',
            args: { s3_uri: s3_uri },
            callback: function(r) {
                if (r.message && r.message.url) {
                    window.open(r.message.url, '_blank');
                }
            },
            error: function(r) {
                frappe.msgprint(__('Failed to generate download URL. Check AWS credentials in site config.'));
            }
        });
    } else {
        // For non-S3 URLs, open directly
        window.open(s3_uri, '_blank');
    }
}

frappe.ui.form.on('Agent Log', {
    refresh: function(frm) {
        // Add "Open Video" button if video_url exists
        if (frm.doc.video_url) {
            frm.add_custom_button(__('Video Recording'), function() {
                open_s3_url(frm.doc.video_url);
            }, __('View Proofs'));
        }

        // Add "Open Screenshot" button if screenshot_url exists
        if (frm.doc.screenshot_url) {
            frm.add_custom_button(__('Screenshot'), function() {
                open_s3_url(frm.doc.screenshot_url);
            }, __('View Proofs'));
        }

        // Add "Open PDF Certificate" button if pdf_url exists
        if (frm.doc.pdf_url) {
            frm.add_custom_button(__('PDF Certificate'), function() {
                open_s3_url(frm.doc.pdf_url);
            }, __('View Proofs'));
        }

        // Add "Open Proofs Folder" button if proofs_folder exists
        // Note: proofs_folder is an S3 prefix, not a single object - may need S3 console
        if (frm.doc.proofs_folder) {
            frm.add_custom_button(__('All Proofs'), function() {
                // For folder URIs, show a message with the path
                if (frm.doc.proofs_folder.startsWith('s3://')) {
                    frappe.msgprint({
                        title: __('Proofs Folder'),
                        message: __('Proofs are stored at: {0}<br><br>Use AWS Console or CLI to browse.', [frm.doc.proofs_folder]),
                        indicator: 'blue'
                    });
                } else {
                    window.open(frm.doc.proofs_folder, '_blank');
                }
            }, __('View Proofs'));
        }

        // Add "Open Full Replay" button if html_output exists and is demo run
        if (frm.doc.html_output && frm.doc.is_demo_run) {
            frm.add_custom_button(__('Full Replay'), function() {
                // Open HTML in new window
                const newWindow = window.open('', '_blank');
                if (newWindow) {
                    newWindow.document.write(frm.doc.html_output);
                    newWindow.document.close();
                }
            }, __('View Proofs'));
        }

        // Style the HTML output section for better display
        if (frm.doc.html_output) {
            setTimeout(() => {
                const htmlField = frm.fields_dict.html_output;
                if (htmlField && htmlField.$wrapper) {
                    // Add iframe wrapper for better sandboxing
                    const htmlContent = frm.doc.html_output;
                    const iframe = document.createElement('iframe');
                    iframe.style.width = '100%';
                    iframe.style.height = '600px';
                    iframe.style.border = '1px solid var(--border-color)';
                    iframe.style.borderRadius = '8px';
                    iframe.srcdoc = htmlContent;

                    htmlField.$wrapper.find('.like-disabled-input, .html-content').html('');
                    htmlField.$wrapper.find('.like-disabled-input, .html-content').append(iframe);
                }
            }, 100);
        }

        // Add demo run indicator badge
        if (frm.doc.is_demo_run) {
            frm.set_intro(__('This is a Demo Dry Run - no actual warranty was registered.'), 'blue');
        }
    },

    onload: function(frm) {
        // Set up any filters or defaults
        if (frm.doc.is_demo_run) {
            frm.toggle_display('section_break_demo', true);
        }
    }
});
