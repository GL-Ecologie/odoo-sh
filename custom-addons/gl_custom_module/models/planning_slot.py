from odoo import models, fields, api
from odoo.exceptions import ValidationError
import datetime
import logging

# TODO: Remove conditional material assignment


class PlanningSlot(models.Model):
    _inherit = "planning.slot"

    _logger = logging.getLogger(__name__)
    _name = "planning.slot"
    _description = "Custom planning slot (shift) model"

    # OPTIONAL: we can later wire this to an employee/resource pref model
    shift_type_id = fields.Many2one(
        "planning.shift_type",
        string="Shift Type",
    )

    counts_for_max_shift_per_week = fields.Boolean(
        string="Counts for max shift per week?",
        help="When set to False, this shift will not count for max shifts per week of resource (employee)",
        default=True,
    )

    material_type_ids = fields.Many2many(
        "materials.material_type",
        "planning_slot_material_type_rel",
        "shift_id",
        "material_type_id",
        string="Required materials",
    )

    resource_ids_domain = fields.Binary(
        string="Resources domain",
        help="Dynamic domain used for the resource that can be set on shift",
        compute="_compute_resource_domain",
    )

    @api.depends("start_datetime", "shift_type_id", "role_id", "counts_for_max_shift_per_week")
    def _compute_resource_domain(self):
        """Limit resource_id dropdown to people who have not yet reached
        their weekly max number of shifts for the week of start_datetime.
        """

        self._logger.info(f"Compute resource domain for: {len(self)}")
        MAX_FIELD = "max_shifts_per_week"  # <- change if yours is different
        employees = self.env["hr.employee"]
        Slot = self.env["planning.slot"]

        # If we don't have a date yet, don't touch the domain
        shift_candidates = employees.sudo().search([(MAX_FIELD, ">=", 0)])

        self._logger.info(f"Resource list: {shift_candidates}")

        for slot in self:
            if not slot.start_datetime:
                slot.resource_ids_domain = []
                continue
            # Compute week start / end (Monday-based)
            # Assumes start_datetime is already a datetime object in UTC

            start = fields.Datetime.to_datetime(slot.start_datetime)
            # get Monday 00:00 and Sunday 23:59-ish
            week_start = start - datetime.timedelta(days=start.weekday())
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            week_end = week_start + datetime.timedelta(days=7)

            eligible_ids = []
            base_domain = []
            for candidate in shift_candidates:
                resource = candidate.resource_id

                slot._logger.info(
                    f"{candidate.display_name}: {slot.shift_type_id not in candidate.allowed_shift_type_ids}\nShifts employee wants:{candidate.allowed_shift_type_ids}"
                )

                if slot.role_id not in candidate.planning_role_ids or slot.shift_type_id not in candidate.allowed_shift_type_ids:
                    continue

                if (
                    slot._check_employee_availability_conflict(candidate=resource)
                    or slot._check_evening_morning_shift_conflict(candidate=resource)
                    or slot._check_employee_works_weekends_conflict(candidate=resource)
                ):
                    continue

                self._logger.info(f"Candidate {candidate.name} wants {candidate[MAX_FIELD]} max shifts per week")
                max_weekly = getattr(candidate, MAX_FIELD, 0)
                self._logger.info(f"{candidate.name} - max_weekly: {max_weekly}")

                if not max_weekly or max_weekly == 0 or not slot.counts_for_max_shift_per_week:
                    eligible_ids.append(resource.id)
                    continue

                # Count this resource's shifts in the same week
                existing_count = Slot.search_count(
                    [
                        ("resource_id", "=", resource.id),
                        ("start_datetime", ">=", week_start),
                        ("start_datetime", "<", week_end),
                        ("id", "!=", slot.id),  # ignore current record
                    ]
                    + [("counts_for_max_shift_per_week", "=", True)]
                    if slot.counts_for_max_shift_per_week
                    else []
                )
                self._logger.info(f"Existing count for {candidate.name} is {existing_count}")

                if existing_count < max_weekly:
                    eligible_ids.append(resource.id)

            if not eligible_ids:
                # No one eligible → domain that matches nobody
                domain = base_domain + [("id", "=", 0)]
            else:
                domain = base_domain + [("id", "in", eligible_ids)]
            self._logger.info(f"Final domain: {domain}")
            slot.resource_ids_domain = domain

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
            if max_shifts and slot.counts_for_max_shift_per_week:
                week_slots = slot._get_week_slots_for_resource()
                if len(week_slots) >= max_shifts:
                    raise ValidationError(
                        self.env._(
                            "You cannot assign %(resource)s to this shift.\n\n"
                            "Reason: this resource would exceed their maximum "
                            "of %(max)d shifts for this week.",
                            resource=slot.resource_id.display_name,
                            max=max_shifts,
                        )
                    )

            # ---- 2) SHIFT-TYPE PREFERENCE ----
            if slot.shift_type_id and not slot._resource_accepts_shift_type():
                raise ValidationError(
                    self.env._(
                        "You cannot assign %(resource)s to this shift.\n\n" "Reason: this resource has not opted into %(stype)s shifts.",
                        resource=slot.resource_id.display_name,
                        stype=slot.shift_type_id.name,
                    )
                )

            # ---- 3) ROLE TYPE RESTRICTION ----
            if slot.role_id and not slot._resource_suitable_for_shift_role():
                raise ValidationError(
                    self.env._(
                        "You cannot assign %(resource)s to this shift.\n\n" "Reason: this resource can't fill role %(srole)s",
                        resource=slot.resource_id.display_name,
                        srole=slot.role_id.name,
                    )
                )

            # ---- 4) EMPLOYEE EVENING-MORNING SHIFT COMBINATION RESTRICTION ----
            if slot._check_evening_morning_shift_conflict():
                raise ValidationError(
                    self.env._(
                        "You cannot assign %(resource)s to this shift.\n\n"
                        "Reason: this resource doesn't want to combine evening with next morning shifts",
                        resource=slot.resource_id.display_name,
                    )
                )

            # ---- 5) EMPLOYEE WEEKEND AVAILABILITY RESTRICTION ----
            if slot._check_employee_works_weekends_conflict():
                raise ValidationError(
                    self.env._(
                        "You cannot assign %(resource)s to this shift.\n\n" "Reason: this resource doesn't want to work weekends",
                        resource=slot.resource_id.display_name,
                    )
                )

            
            # ---- 6) EMPLOYEE CALENDAR AVAILABILITY RESTRICTION ----
            if slot._check_employee_availability_conflict():
                raise ValidationError(
                    self.env._(
                        "You cannot assign %(resource)s to this shift.\n\n"
                        "Reason: this resource is not marked as available for %(stype)s on %(sdate)s.",
                        resource=slot.resource_id.display_name,
                        stype=slot.shift_type_id.name,
                        sdate=fields.Date.to_string(fields.Date.to_date(slot.start_datetime)),
                    )
                )

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

    def _resource_suitable_for_shift_role(self):
        """
        Returns whether or not the employee can perform that shift role
        """
        self.ensure_one()
        can_perform_role = False
        if not self.role_id or (self.role_id and self.role_id in self.resource_id.employee_id.planning_role_ids):
            can_perform_role = True

        return can_perform_role

    def _check_employee_availability_conflict(self, candidate=None):
        """
        Checks whether this shift conflicts with the employee's explicit availability entry.
        Returns True if the employee is NOT available for this shift/date.
        """
        self.ensure_one()

        resource_being_checked = candidate if candidate else (self.resource_id if self.resource_id else None)

        if not resource_being_checked or not self.start_datetime or not self.shift_type_id:
            return False

        entry_date = fields.Date.to_date(self.start_datetime)

        availability_entry = self.env["planning.employee_availability_entry"].search(
            [
                ("resource_id", "=", resource_being_checked.id),
                ("date", "=", entry_date),
                ("shift_type_id", "=", self.shift_type_id.id),
                ("state", "=", "validated"),
            ],
            limit=1,
        )
        # Strict mode:
        # if there is no explicit entry, employee is treated as unavailable
        if not availability_entry:
            return True

        return not availability_entry.available

    def _check_evening_morning_shift_conflict(self, candidate=None):
        """
        Checks whether this shift violates resource (employee) evening-morning shift combination constraint
        """
        self._logger.info(f"Check evening morning conflict")
        evening_morning_conflict = False

        resource_being_checked = candidate if candidate else (self.resource_id if self.resource_id else None)

        if (
            (resource_being_checked)
            and (not resource_being_checked.employee_id.combine_evening_morning_shift)
            and self.shift_type_id
            and (self.shift_type_id.name.endswith("vening") or self.shift_type_id.name.endswith("orning"))
        ):
            start = self.start_datetime.date()
            self._logger.info(f"shift type {self.shift_type_id.name} Start date {start}")
            if self.shift_type_id.name.endswith("vening"):
                start_date_modifier = +datetime.timedelta(days=1)
                check_against_shift_type = "orning"
            else:
                start_date_modifier = -datetime.timedelta(days=1)
                check_against_shift_type = "vening"
            self._logger.info(f"Date to check against: {start + start_date_modifier}\n Against shift type {check_against_shift_type}")
            domain = [
                ("id", "!=", self.id),
                ("resource_id", "=", resource_being_checked.id),
                ("start_datetime", ">=", start + start_date_modifier),
                ("start_datetime", "<", start + start_date_modifier + datetime.timedelta(days=1)),
                ("shift_type_id.name", "like", check_against_shift_type),
            ]
            self._logger.info(f"Domain: {domain}")
            conflicting_shifts = self.search(domain)
            self._logger.info(f"Result: {len(conflicting_shifts)}")
            evening_morning_conflict = len(conflicting_shifts) > 0

        return evening_morning_conflict

    def _check_employee_works_weekends_conflict(self, candidate=None):
        """
        Checks whether this employee wants to work during the weekends
        """
        weekends_conflict = False

        resource_being_checked = candidate if candidate else (self.resource_id if self.resource_id else None)

        is_friday_evening = (
            self.shift_type_id.name.endswith("vening") and fields.Datetime.to_datetime(self.start_datetime).isoweekday() == 5
        )
        is_monday_morning = (
            self.shift_type_id.name.endswith("orning") and fields.Datetime.to_datetime(self.start_datetime).isoweekday() == 1
        )
        is_weekend = fields.Datetime.to_datetime(self.start_datetime).isoweekday() in [6, 7]

        if (
            resource_being_checked
            and (not resource_being_checked.employee_id.available_to_work_weekends)
            and self.shift_type_id
            and (is_friday_evening or is_monday_morning or is_weekend)
        ):
            weekends_conflict = True
        return weekends_conflict
