# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestHrPayslipAttendanceReportTemplateWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.company = cls.env["res.company"].create({"name": "Test Company"})

        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Test Employee",
                "company_id": cls.company.id,
            }
        )

        cls.template = cls.env.ref(
            "payroll_attendance_report.hr_payslip_attendance_report_template_default"
        )

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
        Wizard = self.env["hr.payslip.attendance.report.template.wizard"].with_context(
            default_payslip_id=self.payslip.id
        )
        wizard = Wizard.create(
            {
                "template_id": self.template.id,
            }
        )

        self.assertTrue(wizard)
        self.assertEqual(wizard.payslip_id, self.payslip)
        self.assertEqual(wizard.template_id, self.template)

    def test_wizard_default_get_template(self):
        view = self.template.report_template_id
        self.env["hr.payslip.attendance.report.template"].create(
            {
                "name": "Attendance Template 2",
                "report_template_id": view.id,
                "active": True,
            }
        )

        defaults = self.env["hr.payslip.attendance.report.template.wizard"].default_get(
            ["template_id"]
        )

        self.assertIn("template_id", defaults)
        self.assertTrue(defaults["template_id"])

    def test_wizard_default_get_payslip_from_context(self):
        Wizard = self.env["hr.payslip.attendance.report.template.wizard"].with_context(
            default_payslip_id=self.payslip.id
        )
        defaults = Wizard.default_get(["payslip_id"])

        self.assertIn("payslip_id", defaults)
        self.assertEqual(defaults["payslip_id"], self.payslip.id)

    def test_wizard_dates_follow_payslip_period(self):
        Wizard = self.env["hr.payslip.attendance.report.template.wizard"].with_context(
            default_payslip_id=self.payslip.id
        )
        wizard = Wizard.create(
            {
                "template_id": self.template.id,
            }
        )

        self.assertEqual(wizard.date_from, self.payslip.date_from)
        self.assertEqual(wizard.date_to, self.payslip.date_to)

    def test_wizard_action_print(self):
        Wizard = self.env["hr.payslip.attendance.report.template.wizard"].with_context(
            default_payslip_id=self.payslip.id
        )
        wizard = Wizard.create(
            {
                "template_id": self.template.id,
            }
        )

        result = wizard.action_print()

        self.assertIsInstance(result, dict)
        self.assertIn("type", result)
