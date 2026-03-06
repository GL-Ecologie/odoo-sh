from odoo import models, fields, api, _
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

    def write(self, vals):
        """
        Redirect writes for our custom fields to the real hr.employee record,
        and DO NOT let the ORM try to update the hr_employee_public SQL view.
        """
        emp_field_names = {
            "allowed_shift_type_ids",
            "max_shifts_per_week",
            "combine_evening_morning_shift",
        }

        # Split vals: what we care about vs everything else
        emp_vals = {k: v for k, v in vals.items() if k in emp_field_names}
        other_vals = {k: v for k, v in vals.items() if k not in emp_field_names}

        if emp_vals:
            # propagate to the real employees, bypassing public restrictions
            self.mapped("employee_id").write(emp_vals)

        # For safety, just ignore writes to the SQL view itself.
        # If you *know* some other public fields need to be updatable, we can
        # handle those explicitly later.
        if other_vals:
            # You *could* log this to spot unexpected writes:
            _logger.info("Ignoring write on hr.employee.public: %s", other_vals)
            pass

        return True
    #@api.onchange('allowed_shift_type_ids', 'max_shifts_per_week','combine_evening_morning_shift')
    #def _onchange_planning_fields(self):
    #    _logger.info(f"Public employee changed a custom field. Applying update to related employee")
    #    
    #    self.employee_id.allowed_shift_type_ids = self.allowed_shift_type_ids
    #    self.employee_id.max_shifts_per_week = self.max_shifts_per_week
    #    self.employee_id.combine_evening_morning_shift = self.combine_evening_morning_shift


    