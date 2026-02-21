# Copyright 2025 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Payroll Attendance Report",
    "summary": """Custom attendance (timesheet) reports for
    payslips with template selection""",
    "version": "16.0.1.0.0",
    "author": "Escodoo",
    "website": "https://github.com/Escodoo/escodoo-addons",
    "license": "AGPL-3",
    "depends": [
        "payroll",
        "hr_attendance",
        "payroll_report",
    ],
    "data": [
        "security/ir.model.access.csv",
        "report/report_templates.xml",
        "data/report_action.xml",
        "data/hr_payslip_attendance_report_template_data.xml",
        "views/hr_payslip_attendance_report_template_views.xml",
        "wizard/hr_payslip_attendance_report_template_wizard_views.xml",
        "views/hr_payslip_form_inherit_attendance_views.xml",
    ],
    "installable": True,
}
