# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrPayslipAttendanceReportTemplateWizard(models.TransientModel):
    _name = "hr.payslip.attendance.report.template.wizard"
    _description = "Payslip Attendance Template Selection Wizard"

    payslip_id = fields.Many2one(
        string="Payslip",
        comodel_name="hr.payslip",
        required=True,
    )
    template_id = fields.Many2one(
        string="Template",
        comodel_name="hr.payslip.attendance.report.template",
        required=True,
        domain=[("active", "=", True)],
    )
    date_from = fields.Date(
        string="Start Date",
        related="payslip_id.date_from",
        readonly=True,
        store=False,
    )
    date_to = fields.Date(
        string="End Date",
        related="payslip_id.date_to",
        readonly=True,
        store=False,
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if "payslip_id" in fields_list and not res.get("payslip_id"):
            payslip_id = self.env.context.get(
                "default_payslip_id"
            ) or self.env.context.get("active_id")
            if payslip_id:
                res["payslip_id"] = payslip_id
        if "template_id" in fields_list and not res.get("template_id"):
            first_template = self.env["hr.payslip.attendance.report.template"].search(
                [("active", "=", True)],
                limit=1,
                order="id",
            )
            if first_template:
                res["template_id"] = first_template.id
        return res

    def action_print(self):
        self.ensure_one()
        if not self.template_id.report_template_id:
            return False

        template_key = self.template_id.report_template_id.key

        base_report = self.env["ir.actions.report"].search(
            [
                ("model", "=", "hr.payslip"),
                (
                    "report_name",
                    "=",
                    "payroll_attendance_report.report_payslip_attendance_br",
                ),
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
                or "'Attendance - %s' % (object.employee_id.name or 'No name')",
            }
        )

        result = temp_report.with_context(
            attendance_date_from=self.date_from,
            attendance_date_to=self.date_to,
        ).report_action(self.payslip_id)
        return result
