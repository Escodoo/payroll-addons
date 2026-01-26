# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestHrPayslipReportTemplateWizard(TransactionCase):
    """Test cases for hr.payslip.report.template.wizard model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.company = cls.env["res.company"].create(
            {
                "name": "Test Company",
            }
        )

        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Test Employee",
                "company_id": cls.company.id,
            }
        )

        # Use default payslip template from data
        cls.template = cls.env.ref("payroll_report.hr_payslip_report_template_default")

        # Minimal payslip structure for tests
        # Use any existing salary structure if available, otherwise create a simple one
        struct = cls.env["hr.payroll.structure"].search([], limit=1)
        if not struct:
            struct = cls.env["hr.payroll.structure"].create(
                {
                    "name": "Test Structure",
                    "type_id": cls.env.ref(
                        "payroll.hr_payroll_structure_type_employee"
                    ).id,
                }
            )

        cls.payslip = cls.env["hr.payslip"].create(
            {
                "name": "Test Payslip",
                "employee_id": cls.employee.id,
                "company_id": cls.company.id,
                "struct_id": struct.id,
                "date_from": "2025-01-01",
                "date_to": "2025-01-31",
            }
        )

    def test_wizard_creation(self):
        """Test wizard creation."""
        wizard = self.env["hr.payslip.report.template.wizard"].create(
            {
                "payslip_id": self.payslip.id,
                "template_id": self.template.id,
            }
        )

        self.assertTrue(wizard)
        self.assertEqual(wizard.payslip_id, self.payslip)
        self.assertEqual(wizard.template_id, self.template)

    def test_wizard_default_get_template(self):
        """Test wizard default_get sets first active template."""
        # Create another active template
        view = self.template.report_template_id
        self.env["hr.payslip.report.template"].create(
            {
                "name": "Template 2",
                "report_template_id": view.id,
                "active": True,
            }
        )

        defaults = self.env["hr.payslip.report.template.wizard"].default_get(
            ["template_id"]
        )

        self.assertIn("template_id", defaults)
        self.assertTrue(defaults["template_id"])

    def test_wizard_default_get_payslip_id_from_context(self):
        """Test wizard default_get sets payslip_id from context."""
        Wizard = self.env["hr.payslip.report.template.wizard"].with_context(
            default_payslip_id=self.payslip.id
        )
        defaults = Wizard.default_get(["payslip_id"])

        self.assertIn("payslip_id", defaults)
        self.assertEqual(defaults["payslip_id"], self.payslip.id)

    def test_wizard_action_print(self):
        """Test wizard action_print."""
        wizard = self.env["hr.payslip.report.template.wizard"].create(
            {
                "payslip_id": self.payslip.id,
                "template_id": self.template.id,
            }
        )

        result = wizard.action_print()

        self.assertIsInstance(result, dict)
        self.assertIn("type", result)
        # last template used should be stored on payslip
        self.assertEqual(self.payslip.last_payslip_template_id, self.template)

    def test_wizard_action_print_no_template_view(self):
        """Test wizard action_print when template has no view."""
        view = self.template.report_template_id
        template_test = self.env["hr.payslip.report.template"].create(
            {
                "name": "Test Template No View",
                "report_template_id": view.id,
            }
        )

        # Remove view to simulate broken configuration
        template_test.report_template_id = False

        wizard = self.env["hr.payslip.report.template.wizard"].create(
            {
                "payslip_id": self.payslip.id,
                "template_id": template_test.id,
            }
        )

        result = wizard.action_print()
        self.assertFalse(result)

    def test_wizard_action_print_no_base_report(self):
        """Test wizard action_print when base report does not exist."""
        wizard = self.env["hr.payslip.report.template.wizard"].create(
            {
                "payslip_id": self.payslip.id,
                "template_id": self.template.id,
            }
        )

        # Delete base payslip report
        base_report = self.env["ir.actions.report"].search(
            [
                ("model", "=", "hr.payslip"),
                ("report_name", "=", "payroll.report_payslip"),
            ],
            limit=1,
        )
        if base_report:
            base_report.unlink()

        result = wizard.action_print()
        self.assertFalse(result)
