# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class HrPayslipRunReportTemplateWizard(models.TransientModel):
    _name = "hr.payslip.run.report.template.wizard"
    _description = "Payslip Batch Conference Template Selection Wizard"

    payslip_run_id = fields.Many2one(
        string="Payslip Batch",
        comodel_name="hr.payslip.run",
        required=True,
    )
    template_id = fields.Many2one(
        string="Template",
        comodel_name="hr.payslip.run.report.template",
        required=True,
        domain=[("active", "=", True)],
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        run_id = self.env.context.get("default_payslip_run_id") or self.env.context.get(
            "active_id"
        )
        if run_id:
            run = self.env["hr.payslip.run"].browse(run_id)
            if "payslip_run_id" in fields_list:
                res["payslip_run_id"] = run.id

        if "template_id" in fields_list and not res.get("template_id"):
            template = self.env["hr.payslip.run.report.template"].search(
                [("active", "=", True)],
                limit=1,
                order="id",
            )
            if template:
                res["template_id"] = template.id

        return res

    def action_print(self):
        self.ensure_one()
        if not self.template_id.report_template_id:
            return False

        template_key = self.template_id.report_template_id.key

        base_report = self.env["ir.actions.report"].search(
            [
                ("model", "=", "hr.payslip.run"),
                (
                    "report_name",
                    "=",
                    "payroll_payslip_report.report_payslip_run_conference",
                ),
            ],
            limit=1,
        )
        if not base_report:
            return False

        temp_report = self.env["ir.actions.report"].create(
            {
                "name": f"{base_report.name} - {self.template_id.name}",
                "model": "hr.payslip.run",
                "report_type": "qweb-pdf",
                "report_name": template_key,
                "print_report_name": base_report.print_report_name
                or "'Payslip Batch Conference - %s' % (object.name or '')",
            }
        )

        result = temp_report.report_action(self.payslip_run_id)
        temp_report.unlink()
        return result
