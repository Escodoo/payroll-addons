# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestHrPayslipAttendanceReportTemplate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.default_view = cls.env.ref(
            "payroll_attendance_report.report_payslip_attendance_br"
        )
        cls.default_report = cls.env.ref(
            "payroll_attendance_report.action_report_payslip_attendance_br"
        )
        cls.template = cls.env["hr.payslip.attendance.report.template"].create(
            {
                "name": "Test Attendance Template",
                "report_template_id": cls.default_view.id,
                "description": "Test attendance template description",
                "active": True,
            }
        )

    def test_template_creation(self):
        self.assertTrue(self.template)
        self.assertEqual(self.template.name, "Test Attendance Template")
        self.assertEqual(self.template.report_template_id, self.default_view)
        self.assertTrue(self.template.active)

    def test_template_duplicate(self):
        result = self.template.action_duplicate()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "hr.payslip.attendance.report.template")

        new_template = self.env["hr.payslip.attendance.report.template"].browse(
            result["res_id"]
        )

        self.assertTrue(new_template)
        self.assertEqual(new_template.name, "Test Attendance Template (Copy)")
        self.assertNotEqual(new_template.id, self.template.id)

        new_view = new_template.report_template_id
        self.assertTrue(new_view)
        self.assertNotEqual(new_view.id, self.default_view.id)
        self.assertIn("_copy_", new_view.key)

        new_report = self.env["ir.actions.report"].search(
            [("report_name", "=", new_view.key)], limit=1
        )
        self.assertTrue(new_report)
        self.assertNotEqual(new_report.id, self.default_report.id)

        view_xmlid = self.env["ir.model.data"].search(
            [("model", "=", "ir.ui.view"), ("res_id", "=", new_view.id)], limit=1
        )
        self.assertTrue(view_xmlid)
        self.assertTrue(view_xmlid.noupdate)

        report_xmlid = self.env["ir.model.data"].search(
            [("model", "=", "ir.actions.report"), ("res_id", "=", new_report.id)],
            limit=1,
        )
        self.assertTrue(report_xmlid)
        self.assertTrue(report_xmlid.noupdate)

    def test_template_duplicate_no_report(self):
        new_view = self.default_view.copy(
            {"key": "payroll_attendance_report.test_view_no_report"}
        )

        self.env["ir.model.data"].create(
            {
                "module": "payroll_attendance_report",
                "name": "test_view_no_report",
                "model": "ir.ui.view",
                "res_id": new_view.id,
            }
        )

        template_no_report = self.env["hr.payslip.attendance.report.template"].create(
            {
                "name": "Template Without Report",
                "report_template_id": new_view.id,
            }
        )

        result = template_no_report.action_duplicate()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "hr.payslip.attendance.report.template")

    def test_template_active_toggle(self):
        self.assertTrue(self.template.active)
        self.template.active = False
        self.assertFalse(self.template.active)
        self.template.active = True
        self.assertTrue(self.template.active)
