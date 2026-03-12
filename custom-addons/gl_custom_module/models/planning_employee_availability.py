from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta

class PlanningEmployeeAvailabilityEntry(models.Model):
    """
    This model represents one day of employee calendar availability
    """
    _inherit = ["mail.thread",  "mail.activity.mixin"]
        
    _name = "planning.employee_availability_entry"
    _description = "Employee planning availability entry"
    _order = "date desc, resource_id, shift_type_id"

    name = fields.Char(compute="_compute_name", store=True)

    resource_id = fields.Many2one("resource.resource", ondelete="cascade", index=True, required=True, export_string_translation=False)

    date = fields.Date(help="The date of this entry", required=True, index=True)

    shift_type_id = fields.Many2one("planning.shift_type", string="Shift type", required=True, ondelete="restrict", index=True)

    available = fields.Boolean(help="Employee available to work this shift and date?", default=False)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("validation_requested", "Validation requested"),
            ("validated", "Validated"),
        ],
        string="Status",
        default="draft",
        tracking=True,
        required=True,
    )

    notes = fields.Char(
        help="Additional information?",
    )

    _sql_constraints = [
        (
            "unique_employee_date_shift",
            "unique(resource_id, date, shift_type_id)",
            "Only one availability entry is allowed per resource, date, and shift type.",
        )
    ]

    @api.depends("resource_id", "date", "shift_type_id", "available", "state")
    def _compute_name(self):
        for rec in self:
            shift = rec.shift_type_id.name or ""
            availability = "Yes" if rec.available else "No"

            state_label = {
                "draft": "Draft",
                "validation_requested": "Pending",
                "validated": "Valid",
            }.get(rec.state, "")

            rec.name = f"{shift} | {availability} | {state_label}"

    def action_request_validation(self):
        entries = self.filtered(lambda r: r.state == "draft")

        if not entries:
            raise UserError(self.env._("There are no draft availability entries to submit for validation."))

        entries.write({"state": "validation_requested"})

        manager_group = self.env.ref("planning.group_planning_manager")
        managers = manager_group.user_ids
        
        for entry in entries:
            entry.message_post(
                body=self.env._("Validation requested for this availability entry.")
            )
            for manager in managers:
                entry.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=manager.id,
                    note=self.env._("Please review this employee availability entry."),
                    date_deadline=fields.Date.today() + timedelta(days=3)
                )

    def action_validate(self):
        if not self.env.user.has_group("planning.group_planning_manager"):
            raise UserError(self.env._("Only Planning Managers can validate availability entries."))

        entries = self.filtered(lambda r: r.state == "validation_requested")

        if not entries:
            raise UserError(self.env._("There are no availability entries waiting for validation."))

        entries.write({"state": "validated"})

        for rec in entries:
            rec.message_post(
                body=self.env._("Availability entry validated.")
            )
            if rec.resource_id.user_id:
                rec.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=rec.resource_id.user_id.id,
                    note=self.env._("Your availability entry has been validated."),
                )

    def action_reset_to_draft(self):
        if not self.env.user.has_group("planning.group_planning_manager"):
            raise UserError(self.env._("Only Planning Managers can reset availability entries to draft."))

        entries = self.filtered(lambda r: r.state in ("validation_requested", "validated"))

        if not entries:
            raise UserError(self.env._("There are no availability entries to reset to draft."))

        entries.write({"state": "draft"})