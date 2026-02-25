from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PlanningSlot(models.Model):
    _inherit = "planning.slot"
    
    _name = 'planning.slot'
    _description = 'Custom planning slot (shift) model'

    # OPTIONAL: we can later wire this to an employee/resource pref model
    x_shift_type = fields.Selection(
        [
            ("morning", "Morning"),
            ("afternoon", "Afternoon"),
            ("evening", "Evening"),
            ("night", "Night"),
        ],
        string="Shift Type",
        help="Custom shift type used for planning constraints.",
    )

    # OPTIONAL helper: just to debug/see when the rule is violated
    x_exceeds_weekly_limit = fields.Boolean(
        string="Exceeds Weekly Limit",
        compute="_compute_exceeds_weekly_limit",
        store=False,
    )

    @api.depends("start_datetime", "end_datetime", "resource_id")
    def _compute_exceeds_weekly_limit(self):
        for slot in self:
            slot.x_exceeds_weekly_limit = False
            if not slot.resource_id or not slot.start_datetime:
                continue

            max_shifts = slot._get_resource_max_shifts_per_week()
            if not max_shifts:
                continue

            week_slots = slot._get_week_slots_for_resource()
            slot.x_exceeds_weekly_limit = len(week_slots) > max_shifts

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
                if len(week_slots) > max_shifts:
                    raise ValidationError(_(
                        "You cannot assign %(resource)s to this shift.\n\n"
                        "Reason: this resource would exceed their maximum "
                        "of %(max)d shifts for this week.",
                        resource=slot.resource_id.display_name,
                        max=max_shifts,
                    ))

            # ---- 2) SHIFT-TYPE PREFERENCE ----
            if slot.x_shift_type and not slot._resource_accepts_shift_type():
                raise ValidationError(_(
                    "You cannot assign %(resource)s to this shift.\n\n"
                    "Reason: this resource has not opted into %(stype)s shifts.",
                    resource=slot.resource_id.display_name,
                    stype=slot.x_shift_type,
                ))

    # ------------- HELPERS (we'll plug into your existing fields later) -------------

    def _get_week_slots_for_resource(self):
        """Return all slots for the same resource in the same calendar week."""
        self.ensure_one()
        if not self.start_datetime or not self.resource_id:
            return self

        start = fields.Datetime.to_datetime(self.start_datetime)
        # get Monday 00:00 and Sunday 23:59-ish
        week_start = start - fields.relativedelta(days=start.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + fields.relativetime(days=7)

        domain = [
            ("id", "!=", self.id),
            ("resource_id", "=", self.resource_id.id),
            ("start_datetime", ">=", week_start),
            ("start_datetime", "<", week_end),
        ]
        return self.search(domain)

    def _get_resource_max_shifts_per_week(self):
        """
        Placeholder: get max shifts from resource/employee.
        For now returns a fixed value so we can test the mechanics.
        Later we’ll replace this with your real preference field.
        """
        self.ensure_one()
        # TODO: replace with something like:
        # return self.resource_id.employee_id.x_max_shifts_per_week
        return 5

    def _resource_accepts_shift_type(self):
        """
        Placeholder: check if the resource has opted into this shift type.
        Later we’ll map this to whatever model/fields you already have.
        """
        self.ensure_one()
        if not self.x_shift_type:
            return True

        # TODO: replace with real logic, e.g. booleans on employee:
        # emp = self.resource_id.employee_id
        # if self.x_shift_type == "morning":
        #     return emp.x_wants_morning
        # ...
        return True