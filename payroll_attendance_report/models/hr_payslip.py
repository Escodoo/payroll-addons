# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def _get_attendances_for_period(self, date_from, date_to):
        self.ensure_one()
        if not self.employee_id or not date_from or not date_to:
            return self.env["hr.attendance"]
        return self.env["hr.attendance"].search(
            [
                ("employee_id", "=", self.employee_id.id),
                ("check_in", ">=", date_from),
                ("check_in", "<=", date_to),
            ],
            order="check_in ASC",
        )
