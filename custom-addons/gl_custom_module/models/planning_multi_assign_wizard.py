import datetime
import logging

import pytz

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PlanningMultiAssignWizard(models.TransientModel):
    _name = "planning.multi_assign_wizard"
    _description = "Multi-resource shift assignment / bulk edit wizard"

    mode = fields.Selection(
        [("create", "Create Shifts"), ("edit", "Edit Shifts")],
        default="create",
        required=True,
    )

    # ── Slot fields ──────────────────────────────────────────────────────────
    # Used as the definition for new slots (create mode) or as the values
    # to write to existing slots (edit mode, opt-in per field).

    template_id = fields.Many2one(
        "planning.slot.template",
        string="Shift Template",
        help="Selecting a template fills in the start/stop times and role automatically.",
    )
    start_datetime = fields.Datetime(string="Start")
    end_datetime = fields.Datetime(string="Stop")
    project_id = fields.Many2one("project.project", string="Project")
    task_id = fields.Many2one(
        "project.task",
        string="Task",
        domain="[('project_id', '=', project_id)]",
    )
    role_id = fields.Many2one("planning.role", string="Role")
    shift_type_id = fields.Many2one("planning.shift_type", string="Shift Type")
    counts_for_max_shift_per_week = fields.Boolean(
        string="Counts for max shift per week?",
        default=True,
    )
    material_type_ids = fields.Many2many(
        "materials.material_type",
        "planning_multi_assign_wizard_material_type_rel",
        "wizard_id",
        "material_type_id",
        string="Required materials",
    )
    reminder = fields.Text(
        string="Reminder / Preparation note",
        help="Preparation note sent to the assigned employee 24h before the shift.",
    )
    date_outside_protocol_window = fields.Boolean(
        compute="_compute_date_outside_protocol_window",
        store=False,
    )

    # ── Edit mode: selected shifts ────────────────────────────────────────────

    slot_ids = fields.Many2many(
        "planning.slot",
        "planning_multi_assign_wizard_slot_rel",
        "wizard_id",
        "slot_id",
        string="Shifts to edit",
    )

    # Opt-in booleans — only ticked fields are written in edit mode
    update_start_datetime = fields.Boolean(string="Update start")
    update_end_datetime = fields.Boolean(string="Update stop")
    update_project_id = fields.Boolean(string="Update project")
    update_task_id = fields.Boolean(string="Update task")
    update_role_id = fields.Boolean(string="Update role")
    update_shift_type_id = fields.Boolean(string="Update shift type")
    update_counts_for_max_shift_per_week = fields.Boolean(string="Update weekly cap flag")
    update_material_type_ids = fields.Boolean(string="Update required materials")
    update_reminder = fields.Boolean(string="Update reminder / preparation note")

    # ── Create mode: resource selection ──────────────────────────────────────

    available_resource_ids = fields.Many2many(
        "resource.resource",
        compute="_compute_available_resources",
        string="Available Resources",
    )

    selected_resource_ids = fields.Many2many(
        "resource.resource",
        "planning_multi_assign_wizard_selected_resource_rel",
        "wizard_id",
        "resource_id",
        string="Assign to",
    )

    # Shown after a partial-success creation (some resources skipped)
    creation_summary = fields.Html(string="Result", readonly=True)

    # ── Template onchange ─────────────────────────────────────────────────────

    @api.onchange("template_id")
    def _onchange_template_id(self):
        """Apply template times to start/end datetime and auto-set role."""
        if not self.template_id:
            return

        tmpl = self.template_id

        # Auto-set role from template
        if tmpl.role_id:
            self.role_id = tmpl.role_id

        # Determine the base date: keep user's current date selection or use today
        if self.start_datetime:
            # Work in user's timezone to preserve the chosen date
            tz = pytz.timezone(self.env.user.tz or "UTC")
            base_date = fields.Datetime.context_timestamp(self, self.start_datetime).date()
        else:
            base_date = fields.Date.today()

        # Convert float start_time / end_time to hours + minutes
        start_h, start_m = _float_to_hm(tmpl.start_time)
        end_h, end_m = _float_to_hm(tmpl.end_time)

        duration_days = max(tmpl.duration_days or 1, 1)
        end_date = base_date + datetime.timedelta(days=duration_days - 1)

        # Build naive local datetimes and convert to UTC for storage
        tz = pytz.timezone(self.env.user.tz or "UTC")
        local_start = datetime.datetime(
            base_date.year, base_date.month, base_date.day, start_h, start_m
        )
        local_end = datetime.datetime(
            end_date.year, end_date.month, end_date.day, end_h, end_m
        )
        self.start_datetime = tz.localize(local_start).astimezone(pytz.UTC).replace(tzinfo=None)
        self.end_datetime = tz.localize(local_end).astimezone(pytz.UTC).replace(tzinfo=None)

    # ── Compute: protocol visit window warning ────────────────────────────────

    @api.depends("task_id", "start_datetime")
    def _compute_date_outside_protocol_window(self):
        for wizard in self:
            if not wizard.task_id or not wizard.start_datetime:
                wizard.date_outside_protocol_window = False
                continue
            temp_slot = self.env["planning.slot"].new(
                {
                    "task_id": wizard.task_id.id,
                    "start_datetime": wizard.start_datetime,
                }
            )
            wizard.date_outside_protocol_window = temp_slot._is_outside_protocol_window()

    # ── Compute: eligible resources ───────────────────────────────────────────

    @api.depends(
        "start_datetime", "role_id", "shift_type_id",
        "counts_for_max_shift_per_week", "project_id",
    )
    def _compute_available_resources(self):
        for wizard in self:
            if not wizard.start_datetime or not wizard.shift_type_id or not wizard.role_id:
                wizard.available_resource_ids = self.env["resource.resource"]
                continue

            # Create an in-memory planning.slot to reuse _compute_resource_domain
            # without duplicating the eligibility logic here.
            temp_slot = self.env["planning.slot"].new(
                {
                    "start_datetime": wizard.start_datetime,
                    "end_datetime": wizard.end_datetime or wizard.start_datetime,
                    "shift_type_id": wizard.shift_type_id.id,
                    "role_id": wizard.role_id.id,
                    "counts_for_max_shift_per_week": wizard.counts_for_max_shift_per_week,
                    "project_id": wizard.project_id.id if wizard.project_id else False,
                }
            )
            temp_slot._compute_resource_domain()
            domain = temp_slot.resource_ids_domain or [("id", "=", 0)]
            wizard.available_resource_ids = self.env["resource.resource"].search(domain)

    # ── Actions to open the wizard ────────────────────────────────────────────

    @api.model
    def action_open_create_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Create Multi-Resource Shifts",
            "res_model": "planning.multi_assign_wizard",
            "view_mode": "form",
            "views": [[False, "form"]],
            "target": "new",
            "context": {"default_mode": "create"},
        }

    @api.model
    def action_open_edit_wizard(self):
        active_ids = self.env.context.get("active_ids", [])
        if not active_ids:
            raise UserError(self.env._("No shifts were selected."))

        ctx = {
            "default_mode": "edit",
            "default_slot_ids": [(6, 0, active_ids)],
        }
        # If all selected slots share the same project, pre-populate it so
        # the task domain works even when "Update project" is not ticked.
        slots = self.env["planning.slot"].browse(active_ids)
        common_projects = slots.mapped("project_id")
        if len(common_projects) == 1:
            ctx["default_project_id"] = common_projects.id

        return {
            "type": "ir.actions.act_window",
            "name": "Edit Shifts",
            "res_model": "planning.multi_assign_wizard",
            "view_mode": "form",
            "views": [[False, "form"]],
            "target": "new",
            "context": ctx,
        }

    # ── Confirm ───────────────────────────────────────────────────────────────

    def action_confirm(self):
        self.ensure_one()
        if self.mode == "create":
            return self._confirm_create()
        return self._confirm_edit()

    def _confirm_create(self):
        if not self.selected_resource_ids:
            raise UserError(self.env._("Please select at least one resource."))
        if not self.start_datetime or not self.end_datetime:
            raise UserError(self.env._("Start and stop date/time are required."))

        created_names = []
        errors = []

        for resource in self.selected_resource_ids:
            vals = {
                "resource_id": resource.id,
                "start_datetime": self.start_datetime,
                "end_datetime": self.end_datetime,
                "project_id": self.project_id.id if self.project_id else False,
                "task_id": self.task_id.id if self.task_id else False,
                "role_id": self.role_id.id if self.role_id else False,
                "shift_type_id": self.shift_type_id.id if self.shift_type_id else False,
                "counts_for_max_shift_per_week": self.counts_for_max_shift_per_week,
                "material_type_ids": [(6, 0, self.material_type_ids.ids)],
            }
            if self.reminder:
                vals["x_studio_reminder"] = self.reminder

            try:
                self.env["planning.slot"].create(vals)
                created_names.append(resource.name)
            except ValidationError as exc:
                msg = str(exc.args[0]).replace("\n", " ")
                errors.append(f"<li><b>{resource.name}</b>: {msg}</li>")

        if errors:
            created_lines = "".join(f"<li>{n}</li>" for n in created_names)
            skipped_lines = "".join(errors)
            self.creation_summary = (
                f"<p><b>{len(created_names)} shift(s) created:</b></p>"
                f"<ul>{created_lines}</ul>"
                f"<p>The following resources were <b>skipped</b> due to constraint violations:</p>"
                f"<ul>{skipped_lines}</ul>"
            )
            return {
                "type": "ir.actions.act_window",
                "res_model": "planning.multi_assign_wizard",
                "res_id": self.id,
                "view_mode": "form",
                "views": [[False, "form"]],
                "target": "new",
            }

        return {"type": "ir.actions.act_window_close"}

    def _confirm_edit(self):
        if not self.slot_ids:
            raise UserError(self.env._("No shifts to edit."))

        vals = {}
        if self.update_start_datetime and self.start_datetime:
            vals["start_datetime"] = self.start_datetime
        if self.update_end_datetime and self.end_datetime:
            vals["end_datetime"] = self.end_datetime
        if self.update_project_id:
            vals["project_id"] = self.project_id.id if self.project_id else False
        if self.update_task_id:
            vals["task_id"] = self.task_id.id if self.task_id else False
        if self.update_role_id:
            vals["role_id"] = self.role_id.id if self.role_id else False
        if self.update_shift_type_id:
            vals["shift_type_id"] = self.shift_type_id.id if self.shift_type_id else False
        if self.update_counts_for_max_shift_per_week:
            vals["counts_for_max_shift_per_week"] = self.counts_for_max_shift_per_week
        if self.update_material_type_ids:
            vals["material_type_ids"] = [(6, 0, self.material_type_ids.ids)]
        if self.update_reminder:
            vals["x_studio_reminder"] = self.reminder or False

        if not vals:
            raise UserError(self.env._("No fields were selected for update."))

        self.slot_ids.write(vals)
        return {"type": "ir.actions.act_window_close"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _float_to_hm(value):
    """Convert a float hour value (e.g. 8.5) to (hours, minutes)."""
    value = value or 0.0
    h = int(value)
    m = round((value - h) * 60)
    # Guard against rounding to 60
    if m == 60:
        h += 1
        m = 0
    return h, m
