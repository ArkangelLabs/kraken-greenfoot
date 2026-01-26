// Copyright (c) 2024, Kraken and contributors
// For license information, please see license.txt

frappe.ui.form.on('Warranty Registration', {
    refresh: function(frm) {
        // Form refresh handler
    }
});

// List View settings
frappe.listview_settings['Warranty Registration'] = {
    add_fields: ['brand', 'processing_status'],
    get_indicator: function(doc) {
        if (doc.processing_status === 'Completed') {
            return [__('Completed'), 'green', 'processing_status,=,Completed'];
        } else if (doc.processing_status === 'Failed') {
            return [__('Failed'), 'red', 'processing_status,=,Failed'];
        } else if (doc.processing_status === 'Processing') {
            return [__('Processing'), 'orange', 'processing_status,=,Processing'];
        } else {
            return [__('Pending'), 'blue', 'processing_status,=,Pending'];
        }
    }
};
