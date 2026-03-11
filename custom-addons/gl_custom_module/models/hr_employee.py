from odoo import models, fields, _
from odoo.exceptions import UserError

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    allowed_shift_type_ids = fields.Many2many(
        "planning.shift_type",
        "hr_employee_shift_type_rel",   # relation table name
        "employee_id",                  # column on relation table pointing to hr.employee
        "shift_type_id",                # column on relation table pointing to planning.shift.type
        string="Allowed shift types",
        help="Which shift types this employee is willing/allowed to work.",
    )

    # # Todo: implement constraint logic in PlanningSlot
    # max_morning_shifts_per_week = fields.Integer()
    # max_evening_shifts_per_week = fields.Integer()

    max_shifts_per_week = fields.Integer(
        string="Max shifts per week",
        help="How many shifts this employee is willing to work in a week.",
    )

    available_to_work_weekends = fields.Boolean(
        string="Available to work weekends",
        help="Whether this employee is available for weekend shifts (Friday evening to Monday morning)"
    )
    
    combine_evening_morning_shift = fields.Boolean(
        string="Combine evening and morning shifts",
        help="Is employee willing to combine an evening and morning shift in the same day?",
    )

    version_id = fields.Many2one(
        groups="hr.group_hr_user"
    )

    exceptional_location_id = fields.Many2one(
        groups="hr.group_hr_user"
    )

    planning_role_ids = fields.Many2many(
        groups="hr.group_hr_user"
    )