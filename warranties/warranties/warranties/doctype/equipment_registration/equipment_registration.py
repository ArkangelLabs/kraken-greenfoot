# Copyright (c) 2024, Kraken and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EquipmentRegistration(Document):
    def validate(self):
        # Normalize province to uppercase
        if self.province:
            self.province = self.province.upper()
