# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime, time

from odoo import fields, models


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    attendance_date_from = fields.Date(string="Attendance Start Date")
    attendance_date_to = fields.Date(string="Attendance End Date")

    def _get_attendances_for_period(self, date_from, date_to):
        self.ensure_one()

        if not self.employee_id or not date_from or not date_to:
            return self.env["hr.attendance"]

        datetime_from = datetime.combine(date_from, time.min)
        datetime_to = datetime.combine(date_to, time.max)

        return self.env["hr.attendance"].search(
            [
                ("employee_id", "=", self.employee_id.id),
                ("check_in", ">=", datetime_from),
                ("check_in", "<=", datetime_to),
            ],
            order="check_in ASC",
        )
