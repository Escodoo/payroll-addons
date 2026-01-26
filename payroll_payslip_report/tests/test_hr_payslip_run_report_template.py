# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestHrPayslipRunReportTemplate(TransactionCase):
    def setUp(self):
        super().setUp()
        self.template_model = self.env["hr.payslip.run.report.template"]
        self.default_template = self.env.ref(
            "payroll_payslip_report.hr_payslip_run_report_template_default"
        )

    def test_template_duplicate_creates_new_template(self):
        action = self.default_template.action_duplicate()
        self.assertIsInstance(action, dict)
        new_template = self.template_model.browse(action["res_id"])
        self.assertTrue(new_template.exists())
        self.assertNotEqual(new_template.id, self.default_template.id)
        self.assertNotEqual(
            new_template.report_template_id.id,
            self.default_template.report_template_id.id,
        )
        self.assertTrue(
            new_template.report_template_id.key.endswith("_copy_1"),
        )
        self.assertEqual(new_template.name, f"{self.default_template.name} (Copy)")

    def test_template_duplicate_sequential_view_names(self):
        first_copy = self.template_model.browse(
            self.default_template.action_duplicate()["res_id"]
        )
        second_copy = self.template_model.browse(
            first_copy.action_duplicate()["res_id"]
        )
        self.assertTrue(first_copy.report_template_id.name.endswith(" (Copy 1)"))
        self.assertTrue(second_copy.report_template_id.name.endswith(" (Copy 2)"))

    def test_get_conference_data_empty_batch(self):
        payslip_run = self.env["hr.payslip.run"].create(
            {
                "name": "Test Batch",
                "date_start": "2026-01-01",
                "date_end": "2026-01-31",
            }
        )
        data = payslip_run._get_conference_data()
        self.assertEqual(data["total_gross"], 0.0)
        self.assertEqual(data["total_deduction"], 0.0)
        self.assertEqual(data["total_net"], 0.0)
        self.assertEqual(len(data["lines"]), 0)
