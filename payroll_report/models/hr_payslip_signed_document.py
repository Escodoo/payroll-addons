# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class HrPayslipSignedDocument(models.Model):
    _name = "hr.payslip.signed.document"
    _description = "Signed Payslip Document"
    _order = "create_date desc"

    name = fields.Char(string="Document Name", required=True)
    payslip_id = fields.Many2one(
        string="Payslip",
        comodel_name="hr.payslip",
        required=True,
        ondelete="cascade",
    )
    template_id = fields.Many2one(
        string="Template Used",
        comodel_name="hr.payslip.report.template",
        help="Template that was used to generate this signed document",
    )
    attachment = fields.Binary(
        string="Signed Document",
        required=True,
        help="The signed payslip document file",
    )
    attachment_filename = fields.Char(string="Filename")
    date_signed = fields.Date(
        default=fields.Date.today,
        help="Date when the payslip was signed",
    )
    notes = fields.Text()

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if "name" in fields_list and not res.get("name") and res.get("template_id"):
            template = self.env["hr.payslip.report.template"].browse(res["template_id"])
            res["name"] = template.name
        return res

    @api.onchange("template_id")
    def _onchange_template_id(self):
        if self.template_id:
            self.name = self.template_id.name
