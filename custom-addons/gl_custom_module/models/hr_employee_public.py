from odoo import models, fields

class HREmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    allowed_shift_type_ids = fields.Many2many(
        related="employee_id.allowed_shift_type_ids",
        readonly=False,
        string="Allowed shift types",
        related_sudo=True
    )
    
    max_shifts_per_week = fields.Integer(
        string="Max shifts per week",
        related="employee_id.max_shifts_per_week",
        readonly=False,
        related_sudo=True
    )

    combine_evening_morning_shift = fields.Boolean(
        related="employee_id.combine_evening_morning_shift",
        readonly=False,
        string="Combine evening and morning shifts",
        related_sudo=True
    )