# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class HrPayslipRun(models.Model):
    _inherit = "hr.payslip.run"

    def _get_conference_data(self):
        self.ensure_one()
        lines = []
        total_gross = 0.0
        total_deduction = 0.0
        total_net = 0.0
        currency = self.company_id.currency_id

        for slip in self.slip_ids:
            gross = sum(
                line.total
                for line in slip.line_ids
                if line.category_id and line.category_id.code == "LIC" and line.total
            )
            raw_deductions = sum(
                line.total
                for line in slip.line_ids
                if line.category_id and line.category_id.code == "DED" and line.total
            )
            deductions = abs(raw_deductions)
            net = gross - deductions

            total_gross += gross
            total_deduction += deductions
            total_net += net

            bank = slip.employee_id.bank_account_id
            bank_name = bank.bank_id.name if bank and bank.bank_id else ""
            agency = bank.bra_number
            agency_dv = bank.bra_number_dig
            account = bank.acc_number if bank and bank.acc_number else ""
            account_dv = bank.acc_number_dig
            lines.append(
                {
                    "slip": slip,
                    "employee": slip.employee_id,
                    "cpf": slip.employee_id.cpf or "",
                    "bank_name": bank_name,
                    "agency": agency,
                    "agency_dv": agency_dv,
                    "account": account,
                    "account_dv": account_dv,
                    "gross": gross,
                    "deductions": deductions,
                    "net": net,
                }
            )

        return {
            "currency": currency,
            "lines": lines,
            "total_gross": total_gross,
            "total_deduction": total_deduction,
            "total_net": total_net,
        }
