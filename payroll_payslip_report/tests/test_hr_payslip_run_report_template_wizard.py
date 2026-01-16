# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestHrPayslipRunReportTemplateWizard(TransactionCase):
    def setUp(self):
        super().setUp()
        self.wizard_model = self.env["hr.payslip.run.report.template.wizard"]
        self.template_model = self.env["hr.payslip.run.report.template"]
        self.default_template = self.env.ref(
            "payroll_payslip_report.hr_payslip_run_report_template_default"
        )
        self.payslip_run = self.env["hr.payslip.run"].create(
            {
                "name": "Test Batch",
                "date_start": "2026-01-01",
                "date_end": "2026-01-31",
            }
        )

    def test_default_get_sets_defaults(self):
        wizard = self.wizard_model.with_context(active_id=self.payslip_run.id).create(
            {}
        )
        self.assertEqual(wizard.payslip_run_id, self.payslip_run)
        self.assertTrue(wizard.template_id)

    def test_action_print_returns_report_action(self):
        wizard = self.wizard_model.with_context(active_id=self.payslip_run.id).create(
            {}
        )
        action = wizard.action_print()
        self.assertIsInstance(action, dict)
        self.assertEqual(action.get("type"), "ir.actions.act_window")
