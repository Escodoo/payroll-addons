# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class HrPayslipReportTemplateWizard(models.TransientModel):
    _name = "hr.payslip.report.template.wizard"
    _description = "Payslip Template Selection Wizard"

    payslip_id = fields.Many2one(
        string="Payslip",
        comodel_name="hr.payslip",
        required=True,
    )
    template_id = fields.Many2one(
        string="Template",
        comodel_name="hr.payslip.report.template",
        required=True,
        domain=[("active", "=", True)],
    )

    @api.model
    def default_get(self, fields_list):
        """Set default payslip and first active template if available"""
        res = super().default_get(fields_list)
        if "payslip_id" in fields_list and not res.get("payslip_id"):
            payslip_id = self.env.context.get(
                "default_payslip_id"
            ) or self.env.context.get("active_id")
            if payslip_id:
                res["payslip_id"] = payslip_id
        if "template_id" in fields_list:
            first_template = self.env["hr.payslip.report.template"].search(
                [("active", "=", True)],
                limit=1,
                order="id",
            )
            if first_template:
                res["template_id"] = first_template.id
        return res

    def action_print(self):
        """Print payslip using selected template"""
        self.ensure_one()
        if not self.template_id.report_template_id:
            return False

        template_key = self.template_id.report_template_id.key
        base_report = self.env["ir.actions.report"].search(
            [
                ("model", "=", "hr.payslip"),
                ("report_name", "=", "payroll.report_payslip"),
            ],
            limit=1,
        )

        if not base_report:
            return False

        temp_report = self.env["ir.actions.report"].create(
            {
                "name": f"{base_report.name} - {self.template_id.name}",
                "model": "hr.payslip",
                "report_type": "qweb-pdf",
                "report_name": template_key,
                "print_report_name": base_report.print_report_name
                or "'Payslip - %s' % (object.employee_id.name or 'No name')",
            }
        )
        result = temp_report.report_action(self.payslip_id)
        self.payslip_id.last_payslip_template_id = self.template_id
        return result
