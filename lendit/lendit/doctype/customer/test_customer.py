import frappe
from frappe.tests import IntegrationTestCase


class IntegrationTestCustomer(IntegrationTestCase):
    def test_customer_number_is_generated_when_missing(self):
        customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": "Generated Number Test",
                "customer_type": "Individual",
                "status": "Active",
            }
        )
        customer.insert(ignore_permissions=True)

        self.assertRegex(customer.customer_number, r"^CUS-\d{6}$")

    def test_generated_customer_numbers_are_unique(self):
        first = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": "Generated Number Test One",
                "customer_type": "Individual",
                "status": "Active",
            }
        )
        first.insert(ignore_permissions=True)

        second = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": "Generated Number Test Two",
                "customer_type": "Individual",
                "status": "Active",
            }
        )
        second.insert(ignore_permissions=True)

        self.assertNotEqual(first.customer_number, second.customer_number)

    def test_customer_number_cannot_be_changed(self):
        customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": "Immutable Number Test",
                "customer_type": "Individual",
                "status": "Active",
            }
        )
        customer.insert(ignore_permissions=True)

        original_number = customer.customer_number
        customer.customer_name = "Updated Immutable Number Test"
        customer.customer_number = "CUS-999999"

        with self.assertRaises(frappe.ValidationError):
            customer.save(ignore_permissions=True)

        self.assertEqual(
            frappe.db.get_value("Customer", customer.name, "customer_number"),
            original_number,
        )

    def test_duplicate_customer_number_is_rejected(self):
        customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": "Duplicate Number Test One",
                "customer_type": "Individual",
                "customer_number": "CUS-888888",
                "status": "Active",
            }
        )
        customer.insert(ignore_permissions=True)

        duplicate = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": "Duplicate Number Test Two",
                "customer_type": "Individual",
                "customer_number": "CUS-888888",
                "status": "Active",
            }
        )

        with self.assertRaises(frappe.UniqueValidationError):
            duplicate.insert(ignore_permissions=True)

    def test_missing_customer_name_is_rejected(self):
        customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_type": "Individual",
                "status": "Active",
            }
        )

        with self.assertRaises(frappe.ValidationError):
            customer.insert(ignore_permissions=True)

    def test_lendit_staff_cannot_delete_customer(self):
        staff_email = f"lendit-staff-{frappe.generate_hash(length=8)}@example.com"

        frappe.get_doc(
            {
                "doctype": "User",
                "email": staff_email,
                "first_name": "LendIt Staff Test",
                "enabled": 1,
                "send_welcome_email": 0,
                "roles": [{"role": "LendIt Staff"}],
            }
        ).insert(ignore_permissions=True)

        customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_number": f"CUS-PERM-{frappe.generate_hash(length=8)}",
                "customer_name": "Permission Test Customer",
                "customer_type": "Individual",
                "status": "Active",
            }
        ).insert(ignore_permissions=True)

        original_user = frappe.session.user

        try:
            frappe.set_user(staff_email)

            with self.assertRaises(frappe.PermissionError):
                frappe.delete_doc("Customer", customer.name)
        finally:
            frappe.set_user(original_user)

        self.assertTrue(frappe.db.exists("Customer", customer.name))

    def test_lendit_staff_can_create_customer(self):
        staff_email = f"lendit-create-{frappe.generate_hash(length=8)}@example.com"

        frappe.get_doc(
            {
                "doctype": "User",
                "email": staff_email,
                "first_name": "LendIt Staff Create Test",
                "enabled": 1,
                "send_welcome_email": 0,
                "roles": [{"role": "LendIt Staff"}],
            }
        ).insert(ignore_permissions=True)

        customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_number": f"CUS-CREATE-{frappe.generate_hash(length=8)}",
                "customer_name": "Create Permission Test Customer",
                "customer_type": "Individual",
                "status": "Active",
            }
        )

        original_user = frappe.session.user

        try:
            frappe.set_user(staff_email)
            customer.insert()
        finally:
            frappe.set_user(original_user)

        self.assertTrue(frappe.db.exists("Customer", customer.name))

    def test_lendit_staff_can_read_customer(self):
        staff_email = f"lendit-read-{frappe.generate_hash(length=8)}@example.com"

        frappe.get_doc(
            {
                "doctype": "User",
                "email": staff_email,
                "first_name": "LendIt Staff Read Test",
                "enabled": 1,
                "send_welcome_email": 0,
                "roles": [{"role": "LendIt Staff"}],
            }
        ).insert(ignore_permissions=True)

        customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_number": f"CUS-READ-{frappe.generate_hash(length=8)}",
                "customer_name": "Read Permission Test Customer",
                "customer_type": "Individual",
                "status": "Active",
            }
        ).insert(ignore_permissions=True)

        original_user = frappe.session.user

        try:
            frappe.set_user(staff_email)

            customers = frappe.get_list(
                "Customer",
                filters={"name": customer.name},
                fields=["name"],
            )
        finally:
            frappe.set_user(original_user)

        self.assertEqual(len(customers), 1)
        self.assertEqual(customers[0].name, customer.name)

    def test_lendit_staff_can_update_customer(self):
        staff_email = f"lendit-write-{frappe.generate_hash(length=8)}@example.com"

        frappe.get_doc(
            {
                "doctype": "User",
                "email": staff_email,
                "first_name": "LendIt Staff Write Test",
                "enabled": 1,
                "send_welcome_email": 0,
                "roles": [{"role": "LendIt Staff"}],
            }
        ).insert(ignore_permissions=True)

        customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_number": f"CUS-WRITE-{frappe.generate_hash(length=8)}",
                "customer_name": "Original Customer Name",
                "customer_type": "Individual",
                "status": "Active",
            }
        ).insert(ignore_permissions=True)

        original_user = frappe.session.user

        try:
            frappe.set_user(staff_email)
            customer.customer_name = "Updated Customer Name"
            customer.save()
        finally:
            frappe.set_user(original_user)

        updated_customer = frappe.get_doc("Customer", customer.name)

        self.assertEqual(
            updated_customer.customer_name,
            "Updated Customer Name",
        )
