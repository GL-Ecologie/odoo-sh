from odoo import models, fields, api
from odoo.exceptions import ValidationError
import datetime
import logging

# TODO: Remove conditional material assignment


class PlanningSlot(models.Model):
    _inherit = ["planning.slot", "mail.thread"]

    _logger = logging.getLogger(__name__)
    _name = "planning.slot"
    _description = "Custom planning slot (shift) model"

    # OPTIONAL: we can later wire this to an employee/resource pref model
    shift_type_id = fields.Many2one(
        "planning.shift_type",
        string="Shift Type",
    )

    task_id = fields.Many2one(
        "project.task",
        string="Task",
        domain="[('project_id', '=', project_id)]",
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

    date_outside_protocol_window = fields.Boolean(
        compute="_compute_date_outside_protocol_window",
        store=False,
    )

    date_violates_related_visit_gap = fields.Boolean(
        compute="_compute_related_visit_gap",
        store=False,
    )
    related_visit_gap_warning_text = fields.Char(
        compute="_compute_related_visit_gap",
        store=False,
    )

    can_register_hours = fields.Boolean(
        compute="_compute_can_register_hours",
    )

    @api.depends("start_datetime", "shift_type_id", "role_id", "counts_for_max_shift_per_week")
    def _compute_resource_domain(self):
        """Limit resource_id dropdown to people who have not yet reached
        their weekly max number of shifts for the week of start_datetime.
        """

        MAX_FIELD = "max_shifts_per_week"  # <- change if yours is different
        employees = self.env["hr.employee"]
        Slot = self.env["planning.slot"]

        # If we don't have a date yet, don't touch the domain
        shift_candidates = employees.sudo().search([(MAX_FIELD, ">=", 0)])


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

    @api.depends("task_id", "start_datetime", "task_id.x_studio_protocol_visit_single")
    def _compute_date_outside_protocol_window(self):
        for slot in self:
            slot.date_outside_protocol_window = slot._is_outside_protocol_window()

    def _is_outside_protocol_window(self):
        """Returns True if the shift date falls outside the protocol visit window."""
        self.ensure_one()
        if not self.task_id or not self.start_datetime:
            return False

        visit = self.task_id.x_studio_protocol_visit_single
        if not visit:
            return False

        s_day = visit.x_studio_start_day
        s_month = visit.x_studio_start_month
        e_day = visit.x_studio_end_day
        e_month = visit.x_studio_end_month

        if not all([s_day, s_month, e_day, e_month]):
            return False

        shift_date = fields.Datetime.to_datetime(self.start_datetime).date()
        year = shift_date.year

        try:
            window_start = datetime.date(year, int(s_month), int(s_day))
            window_end = datetime.date(year, int(e_month), int(e_day))
        except ValueError:
            return False

        return shift_date < window_start or shift_date > window_end

    @api.depends(
        "task_id", "start_datetime", "project_id",
        "task_id.x_studio_protocol_visit_single",
        "task_id.x_studio_protocol_visit_single.x_studio_related_visit",
        "task_id.x_studio_protocol_visit_single.x_studio_minimum_days_from_previous_visit",
    )
    def _compute_related_visit_gap(self):
        for slot in self:
            violation, message = slot._check_related_visit_gap()
            slot.date_violates_related_visit_gap = violation
            slot.related_visit_gap_warning_text = message

    def _check_related_visit_gap(self):
        """Returns (violation: bool, message: str).

        True when the shift date is fewer than the required minimum days
        after the latest existing shift for the related protocol visit.
        The related visit always points backwards (e.g. HM1 when this
        shift belongs to HM2).
        """
        self.ensure_one()
        if not self.task_id or not self.start_datetime or not self.project_id:
            return False, ""

        visit = self.task_id.x_studio_protocol_visit_single
        if not visit:
            return False, ""

        related_visit = visit.x_studio_related_visit
        min_days = visit.x_studio_minimum_days_from_previous_visit

        if not related_visit or not min_days or min_days <= 0:
            return False, ""

        # Find tasks in the same project linked to the related visit
        related_tasks = self.env["project.task"].search([
            ("project_id", "=", self.project_id.id),
            ("x_studio_protocol_visit_single", "=", related_visit.id),
        ])
        if not related_tasks:
            return False, ""

        # Find their shifts; exclude self if it already has a DB id
        domain = [
            ("task_id", "in", related_tasks.ids),
            ("start_datetime", "!=", False),
        ]
        if self._origin.id:
            domain.append(("id", "!=", self._origin.id))

        related_slots = self.env["planning.slot"].search(domain)
        if not related_slots:
            return False, ""

        latest_related_date = max(
            fields.Datetime.to_datetime(s.start_datetime).date()
            for s in related_slots
        )

        current_date = fields.Datetime.to_datetime(self.start_datetime).date()
        gap = (current_date - latest_related_date).days

        if gap < min_days:
            visit_name = related_visit.x_studio_name or str(related_visit.id)
            message = (
                f"This shift is only {max(gap, 0)} day(s) after the most recent "
                f"{visit_name} shift. The required minimum gap is {min_days} day(s)."
            )
            return True, message

        return False, ""

    @api.depends("resource_id")
    def _compute_can_register_hours(self):
        is_manager = self.env.user.has_group("planning.group_planning_manager")
        for slot in self:
            slot.can_register_hours = is_manager or (slot.resource_id.user_id == self.env.user)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._check_planning_constraints()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._check_planning_constraints()
        return res

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
            and (self.shift_type_id.time_of_day in ("evening", "morning"))
        ):
            start = self.start_datetime.date()
            self._logger.info(f"shift type {self.shift_type_id.name} Start date {start}")
            if self.shift_type_id.time_of_day == "evening":
                start_date_modifier = +datetime.timedelta(days=1)
                check_against_time_of_day = "morning"
            else:
                start_date_modifier = -datetime.timedelta(days=1)
                check_against_time_of_day = "evening"
            self._logger.info(f"Date to check against: {start + start_date_modifier}\n Against time of day: {check_against_time_of_day}")
            domain = [
                ("id", "!=", self.id),
                ("resource_id", "=", resource_being_checked.id),
                ("start_datetime", ">=", start + start_date_modifier),
                ("start_datetime", "<", start + start_date_modifier + datetime.timedelta(days=1)),
                ("shift_type_id.time_of_day", "=", check_against_time_of_day),
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
            self.shift_type_id.time_of_day == "evening" and fields.Datetime.to_datetime(self.start_datetime).isoweekday() == 5
        )
        is_monday_morning = (
            self.shift_type_id.time_of_day == "morning" and fields.Datetime.to_datetime(self.start_datetime).isoweekday() == 1
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

    def action_open_multi_assign_create_wizard(self):
        """Open the multi-resource shift creation wizard.
        Ignores any selected records — always opens a fresh create wizard.
        """
        return self.env["planning.multi_assign_wizard"].action_open_create_wizard()

    def action_open_multi_assign_edit_wizard(self):
        """Open the multi-resource shift edit wizard for the selected shifts.
        Called from the list view <header> button with self = selected records.
        """
        return self.env["planning.multi_assign_wizard"].with_context(
            active_ids=self.ids
        ).action_open_edit_wizard()

    def action_register_timesheet(self):
            """Create a pre-filled timesheet entry for this shift and open it."""
            self.ensure_one()
            if not self.resource_id:
                raise ValidationError(self.env._("Cannot register hours: this shift has no resource assigned."))
            employee = self.resource_id.employee_id
            vals = {
                "name": "/",
                "date": fields.Date.to_date(self.start_datetime) if self.start_datetime else fields.Date.today(),
                "unit_amount": self.allocated_hours or 0.0,
                "x_studio_shift": self.id,
                "employee_id": employee.id
            }
            
            if self.project_id:
                vals["project_id"] = self.project_id.id
            if self.task_id:
                vals["task_id"] = self.task_id.id
            timesheet = self.env["account.analytic.line"].create(vals)
            view_id = self.env.ref("hr_timesheet.timesheet_view_form_user").id
            return {
                "type": "ir.actions.act_window",
                "res_model": "account.analytic.line",
                "res_id": timesheet.id,
                "view_mode": "form",
                "views": [(view_id, "form")],
                "target": "current",
            }