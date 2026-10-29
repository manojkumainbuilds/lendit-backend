import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class Customer(Document):
    def autoname(self):
        # Preserve explicitly supplied numbers for existing integrations
        # and controlled data imports. The frontend will no longer ask
        # staff to enter a number for new customers.
        if not self.customer_number:
            customer_number = make_autoname("CUS-.######")

            # Avoid collisions with numbers already present in the database.
            while frappe.db.exists("Customer", {"customer_number": customer_number}):
                customer_number = make_autoname("CUS-.######")

            self.customer_number = customer_number

    def validate(self):
        # Customer numbers are immutable after creation.
        if self.is_new():
            return

        previous = self.get_doc_before_save()

        if previous and self.customer_number != previous.customer_number:
            frappe.throw(
                "Customer number cannot be changed after creation.",
                frappe.ValidationError,
            )
