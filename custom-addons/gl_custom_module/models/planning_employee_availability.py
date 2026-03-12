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

    _sql_constraints = [
        (
            "unique_employee_date_shift",
            "unique(resource_id, date, shift_type_id)",
            "Only one availability entry is allowed per resource, date, and shift type.",
        )
    ]

    name = fields.Char(compute="_compute_name", store=True)

    resource_id = fields.Many2one("resource.resource", ondelete="cascade", index=True, required=True, export_string_translation=False, default=lambda self: self._default_resource_id())

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


    style_key = fields.Char(
        compute="_compute_style_key"
    )

    @api.model
    def _default_resource_id(self):
        employee = self.env["hr.employee"].search(
            [
                ("user_id", "=", self.env.user.id),
                ("active", "=", True),
                ("resource_id", "!=", False),
            ],
            limit=1,
        )
        return employee.resource_id.id if employee and employee.resource_id else False
        
    @api.depends("state", "available")
    def _compute_style_key(self):
        for rec in self:
            if rec.state == "draft":
                rec.style_key = "draft"
            elif rec.state == "validation_requested" and rec.available:
                rec.style_key = "validation_requested_yes"
            elif rec.state == "validation_requested" and not rec.available:
                rec.style_key = "validation_requested_no"
            elif rec.state == "validated" and rec.available:
                rec.style_key = "validated_yes"
            elif rec.state == "validated" and not rec.available:
                rec.style_key = "validated_no"
            else:
                rec.style_key = "draft"

    @api.depends("resource_id", "date", "shift_type_id")
    def _compute_name(self):
        for rec in self:
            shift = rec.shift_type_id.name or ""

            rec.name = f"{shift}"

    def action_request_validation(self):
        entries = self.filtered(lambda r: r.state in ["draft", "validated"])

        if not entries:
            raise UserError(self.env._("There are no draft or already availability entries to submit for validation."))

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

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)

        draft_records = records.filtered(lambda r: r.state == "draft")
        if draft_records:
            draft_records.action_request_validation()

        return records

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