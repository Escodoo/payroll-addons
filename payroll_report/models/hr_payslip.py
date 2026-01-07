# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    last_payslip_template_id = fields.Many2one(
        string="Last Payslip Template",
        comodel_name="hr.payslip.report.template",
        help="Last template used to print this payslip.",
    )
    signed_document_ids = fields.One2many(
        string="Signed Documents",
        comodel_name="hr.payslip.signed.document",
        inverse_name="payslip_id",
    )
