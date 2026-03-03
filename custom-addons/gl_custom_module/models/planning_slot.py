from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime, logging

#TODO: Update material_unit_assignment_ids domain to show only bookable/available materials

class PlanningSlot(models.Model):
    _inherit = "planning.slot"

    _logger = logging.getLogger(__name__)
    _name = 'planning.slot'
    _description = 'Custom planning slot (shift) model'

    # OPTIONAL: we can later wire this to an employee/resource pref model
    shift_type_id = fields.Many2one(
        'planning.shift_type',
        string="Shift Type",
    )

    material_unit_assignment_ids = fields.Onetomany(
        "materials.material_unit_assignment",
        string="Materials for this shift"
    )
    
    resource_ids_domain = fields.Binary(string="Resources domain", help="Dynamic domain used for the resource that can be set on shift", compute="_compute_resource_domain")
    
    @api.depends('start_datetime', "shift_type_id")
    def _compute_resource_domain(self):
        """Limit resource_id dropdown to people who have not yet reached
        their weekly max number of shifts for the week of start_datetime.
        """
        self.ensure_one()

        # If we don't have a date yet, don't touch the domain
        if not self.start_datetime:
            return {}

        MAX_FIELD = 'max_shifts_per_week'  # <- change if yours is different

        # Compute week start / end (Monday-based)
        # Assumes start_datetime is already a datetime object in UTC

        start = fields.Datetime.to_datetime(self.start_datetime)
        # get Monday 00:00 and Sunday 23:59-ish
        week_start = start - datetime.timedelta(days=start.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + datetime.timedelta(days=7)

        employees = self.env['hr.employee']
        Slot = self.env['planning.slot']

        shift_candidates = employees.search(
            [(MAX_FIELD, ">=", 0)]
        )
        
        self._logger.info(f"Resource list: {shift_candidates}")
        
        eligible_ids = []
        base_domain = []
        for candidate in shift_candidates:
            self._logger.info(f"{candidate.display_name}: {self.shift_type_id not in candidate.allowed_shift_type_ids}\nShifts employee wants:{candidate.allowed_shift_type_ids}")
            
            if self.role_id not in candidate.planning_role_ids or self.shift_type_id not in candidate.allowed_shift_type_ids:
                continue
            
            res = candidate.resource_id
            self._logger.info(f"Candidate {candidate.name} wants {candidate[MAX_FIELD]} max shifts per week")
            max_weekly = getattr(candidate, MAX_FIELD, 0)
            self._logger.info(f"{candidate.name} - max_weekly: {max_weekly}")
            
            if not max_weekly or max_weekly == 0:
                eligible_ids.append(res.id)
                continue

            # Count this resource's shifts in the same week
            existing_count = Slot.search_count([
                ('resource_id', '=', res.id),
                ('start_datetime', '>=', week_start),
                ('start_datetime', '<', week_end),
                ('id', 'not in', self.ids),  # ignore current record
                ('state', '!=', 'cancel'),  # optional
            ])
            self._logger.info(f"Existing count for {candidate.name} is {existing_count}")

            if existing_count < max_weekly:
                eligible_ids.append(res.id)
        
        if not eligible_ids:
            # No one eligible → domain that matches nobody
            domain = base_domain + [('id', '=', 0)]
        else:
            domain = base_domain + [('id', 'in', eligible_ids)]
        self._logger.info(f"Final domain: {domain}")
        self.resource_ids_domain = domain

    # ------------- CONSTRAINT-LIKE LOGIC -------------

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._check_planning_constraints()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._check_planning_constraints()
        return res

    # main checker
    def _check_planning_constraints(self):
        """
        Enforce:
          - resource does not exceed its max desired shifts per week
          - resource is allowed to take this shift type
        """
        for slot in self:
            if not slot.resource_id or not slot.start_datetime:
                continue

            # ---- 1) WEEKLY MAX SHIFTS ----
            max_shifts = slot._get_resource_max_shifts_per_week()
            if max_shifts:
                week_slots = slot._get_week_slots_for_resource()
                if len(week_slots) >= max_shifts:
                    raise ValidationError(_(
                        "You cannot assign %(resource)s to this shift.\n\n"
                        "Reason: this resource would exceed their maximum "
                        "of %(max)d shifts for this week.",
                        resource=slot.resource_id.display_name,
                        max=max_shifts,
                    ))

            # ---- 2) SHIFT-TYPE PREFERENCE ----
            if slot.shift_type_id and not slot._resource_accepts_shift_type():
                raise ValidationError(_(
                    "You cannot assign %(resource)s to this shift.\n\n"
                    "Reason: this resource has not opted into %(stype)s shifts.",
                    resource=slot.resource_id.display_name,
                    stype=slot.shift_type_id.name,
                ))

    # ------------- HELPERS (we'll plug into your existing fields later) -------------

    

    def _get_week_slots_for_resource(self):
        """Return all slots for the same resource in the same calendar week."""
        self.ensure_one()
        if not self.start_datetime or not self.resource_id:
            return self

        start = fields.Datetime.to_datetime(self.start_datetime)
        # get Monday 00:00 and Sunday 23:59-ish
        week_start = start - datetime.timedelta(days=start.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + datetime.timedelta(days=7)

        domain = [
            ("id", "not in", self.ids),
            ("resource_id", "=", self.resource_id.id),
            ("start_datetime", ">=", week_start),
            ("start_datetime", "<", week_end),
            ("state", "!=", "cancelled")
        ]
        
        return self.search(domain)

    def _get_resource_max_shifts_per_week(self):
        """
        Returns the maximum number of shifts an employee has agreed to work in a week.
        """
        self.ensure_one()

        return self.resource_id.employee_id.max_shifts_per_week

    def _resource_accepts_shift_type(self):
        """
        Returns whether or not the employee accepts this type of shift.
        """
        self.ensure_one()

        shift_accepted = False
        
        if not self.shift_type_id or (self.shift_type_id and self.shift_type_id in self.resource_id.employee_id.allowed_shift_type_ids):
            shift_accepted = True

        return shift_accepted

    def _resource_accepts_evening_morning_shift_combination(self):
        """
        Placeholder to implement this logic
        """

        #TODO: implementation
        pass