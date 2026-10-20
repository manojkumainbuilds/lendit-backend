
import frappe
from frappe.tests import IntegrationTestCase


class IntegrationTestCustomer(IntegrationTestCase):
    """Test the Customer DocType's standard validation rules."""

    def test_missing_customer_name_is_rejected(self):
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_number": "CUS-TEST-MISSING-NAME",
            "customer_type": "Individual",
            "status": "Active",
        })

        with self.assertRaises(frappe.exceptions.MandatoryError):
            customer.insert(ignore_permissions=True)

    def test_duplicate_customer_number_is_rejected(self):
        existing_customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_number": "CUS-TEST-DUPLICATE",
            "customer_name": "Original Test Customer",
            "customer_type": "Individual",
            "status": "Active",
        })
        existing_customer.insert(ignore_permissions=True)

        duplicate_customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_number": "CUS-TEST-DUPLICATE",
            "customer_name": "Duplicate Test Customer",
            "customer_type": "Individual",
            "status": "Active",
        })

        with self.assertRaises(frappe.exceptions.UniqueValidationError):
            duplicate_customer.insert(ignore_permissions=True)
