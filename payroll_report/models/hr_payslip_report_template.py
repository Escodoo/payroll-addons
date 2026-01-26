# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, fields, models
from odoo.exceptions import UserError


class HrPayslipReportTemplate(models.Model):
    _name = "hr.payslip.report.template"
    _description = "Payslip Report Template"
    _order = "name"

    name = fields.Char(string="Template Name", required=True)
    active = fields.Boolean(default=True)
    report_template_id = fields.Many2one(
        string="Report Template",
        comodel_name="ir.ui.view",
        domain=[("type", "=", "qweb"), ("key", "like", "payroll_report.%")],
        required=True,
        ondelete="restrict",
    )
    description = fields.Text()

    def action_duplicate(self):
        self.ensure_one()

        original_view = self.report_template_id
        if not original_view:
            raise UserError(_("No report template associated with this template."))
        original_report = self.env["ir.actions.report"].search(
            [("report_name", "=", original_view.key)], limit=1
        )
        if not original_report:
            original_report = self.env["ir.actions.report"].search(
                [
                    ("model", "=", "hr.payslip"),
                    ("report_name", "=", "payroll.report_payslip"),
                ],
                limit=1,
            )
        if not original_report:
            raise UserError(_("Original report action not found for this template."))

        xmlid = self.env["ir.model.data"].search(
            [("model", "=", "ir.ui.view"), ("res_id", "=", original_view.id)],
            limit=1,
        )

        if xmlid:
            module = xmlid.module
            base_name = xmlid.name
        else:
            module = "payroll_report"
            base_name = original_view.key.split(".")[-1]
        index = 1
        while True:
            new_base_name = f"{base_name}_copy_{index}"
            exists = self.env["ir.model.data"].search(
                [("module", "=", module), ("name", "=", new_base_name)], limit=1
            )
            if not exists:
                break
            index += 1
        original_view_name = original_view.name.split(" (Copy")[0]
        copy_index = 1
        while True:
            new_view_name = f"{original_view_name} (Copy {copy_index})"
            exists_name = self.env["ir.ui.view"].search(
                [("name", "=", new_view_name)], limit=1
            )
            if not exists_name:
                break
            copy_index += 1

        new_view_key = f"{module}.{new_base_name}"
        new_view = original_view.copy(
            {
                "name": new_view_name,
                "key": new_view_key,
                "model": original_view.model or "hr.payslip",
            }
        )
        self.env["ir.model.data"].create(
            {
                "module": module,
                "name": new_base_name,
                "model": "ir.ui.view",
                "res_id": new_view.id,
                "noupdate": True,
            }
        )
        new_report = original_report.copy(
            {
                "name": f"{original_report.name} (Copy)",
                "report_name": new_view.key,
                "report_file": new_view.key,
            }
        )

        self.env["ir.model.data"].create(
            {
                "module": module,
                "name": f"{new_base_name}_report",
                "model": "ir.actions.report",
                "res_id": new_report.id,
                "noupdate": True,
            }
        )
        new_template = self.copy(
            {
                "name": f"{self.name} (Copy)",
                "report_template_id": new_view.id,
            }
        )
        return {
            "type": "ir.actions.act_window",
            "name": _("Payslip Template"),
            "res_model": "hr.payslip.report.template",
            "res_id": new_template.id,
            "view_mode": "form",
            "target": "current",
        }
