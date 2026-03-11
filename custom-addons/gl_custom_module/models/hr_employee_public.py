from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)


class HREmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    allowed_shift_type_ids = fields.Many2many(
        related="employee_id.allowed_shift_type_ids",
        readonly=False,
        string="Allowed shift types",
        related_sudo=True,
        store=False
    )
   
    max_shifts_per_week = fields.Integer(
        string="Max shifts per week",
        related="employee_id.max_shifts_per_week",
        readonly=False,
        related_sudo=True,
        store=False
    )

    available_to_work_weekends = fields.Boolean(
        related="employee_id.available_to_work_weekends",
        readonly=False,
        string="Available to work weekends",
        related_sudo=True,
        store=False
    )

    combine_evening_morning_shift = fields.Boolean(
        related="employee_id.combine_evening_morning_shift",
        readonly=False,
        string="Combine evening and morning shifts",
        related_sudo=True,
        store=False
    )
