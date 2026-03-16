from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta
import logging


class PlanningEmployeeAvailabilityEntry(models.Model):
    """
    This model represents one day of employee calendar availability
    """

    _inherit = ["mail.thread", "mail.activity.mixin"]

    _name = "planning.employee_availability_entry"
    _description = "Employee planning availability entry"
    _order = "date desc, resource_id, shift_type_id"

    _logger = logging.getLogger(__name__)

    _unique_employee_date_shift = models.Constraint(
        "UNIQUE(resource_id, date, shift_type_id)",
        "Only one availability entry is allowed per resource, date, and shift type.",
    )

    name = fields.Char(compute="_compute_name", store=True)

    resource_id = fields.Many2one(
        "resource.resource",
        ondelete="cascade",
        index=True,
        required=True,
        export_string_translation=False,
        default=lambda self: self._default_resource_id(),
        domain=[("resource_type", "=", "user")],
    )

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

    style_key = fields.Char(compute="_compute_style_key")

    def _date_range_label(self, dates):
        """Return a human-readable date range string from a list of date objects."""
        min_d = min(dates)
        max_d = max(dates)
        self._logger.info(f"Min date:{min_d}\tMax date:{max_d}")
        if min_d == max_d:
            return min_d.strftime("%d %b %Y")
        return f"{min_d.strftime('%d %b %Y')} - {max_d.strftime('%d %b %Y')}"

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
            shift = rec.shift_type_id.name or "?"
            parts = (rec.resource_id.name or "").split()
            initials = "".join(p[0].upper() for p in parts if p)
            rec.name = f"{initials} - {shift}"

    def action_request_validation(self):

        if not self:
            raise UserError(self.env._("There are no draft or already availability entries to submit for validation."))

        self.write({"state": "validation_requested"})

        for entry in self:
            entry.message_post(body=self.env._("Validation requested for this availability entry."))

        # One activity per manager for the whole batch
        manager_group = self.env.ref("planning.group_planning_manager")
        managers = manager_group.user_ids
        count = len(self)
        date_range = self._date_range_label(self.mapped("date"))
        summary = (
            self.env._("%(count)d availability entries are awaiting your validation (%(range)s).", count=count, range=date_range)
            if count > 1
            else self.env._("Please review this availability entry (%(range)s).", range=date_range)
        )
        for manager in managers:
            self[0].activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=manager.id,
                summary=self.env._(summary),
                date_deadline=fields.Date.today() + timedelta(days=3),
            )

    _REVALIDATION_TRIGGER_FIELDS = {"available", "date", "shift_type_id", "notes"}

    def write(self, vals):
        revalidate = (
            not self.env.context.get("_skip_revalidation")
            and bool(self._REVALIDATION_TRIGGER_FIELDS & vals.keys())
        )
        to_reset = None
        if revalidate:
            to_reset = self.filtered(lambda r: r.state != "draft")

        result = super().write(vals)

        if revalidate:
            if to_reset:
                to_reset.with_context(_skip_revalidation=True).write({"state": "draft"})
            self.action_request_validation()

        return result

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
            rec.message_post(body=self.env._("Availability entry validated."))

        # One activity per affected user for the whole batch
        entries_by_user = {}
        for rec in entries:
            if rec.resource_id.user_id:
                uid = rec.resource_id.user_id.id
                if uid not in entries_by_user:
                    entries_by_user[uid] = {"rep": rec, "count": 0, "dates": []}
                entries_by_user[uid]["count"] += 1
                entries_by_user[uid]["dates"].append(rec.date)

        for uid, data in entries_by_user.items():
            count = data["count"]
            date_range = self._date_range_label(data["dates"])
            message = (
                self.env._("%(count)d of your availability entries have been validated (%(range)s).", count=count, range=date_range)
                if count > 1
                else self.env._("Your availability entry has been validated (%(range)s).", range=date_range)
            )
            user = self.env["res.users"].browse(uid)
            self.env["mail.thread"].message_notify(
                body=message,
                subject="Availability entries validated",
                partner_ids=[
                    user.partner_id.id,
                ],
            )
            self.env["bus.bus"]._sendone(
                user.partner_id,
                "simple_notification",
                {"title": self.env._("Availability validated"), "message": message, "sticky": False},
            )

    def action_reset_to_draft(self):
        if not self.env.user.has_group("planning.group_planning_manager"):
            raise UserError(self.env._("Only Planning Managers can reset availability entries to draft."))

        entries = self.filtered(lambda r: r.state in ("validation_requested", "validated"))

        if not entries:
            raise UserError(self.env._("There are no availability entries to reset to draft."))

        entries.write({"state": "draft"})

        # One activity per affected user for the whole batch
        entries_by_user = {}
        for rec in entries:
            if rec.resource_id.user_id:
                uid = rec.resource_id.user_id.id
                if uid not in entries_by_user:
                    entries_by_user[uid] = {"rep": rec, "count": 0, "dates": []}
                entries_by_user[uid]["count"] += 1
                entries_by_user[uid]["dates"].append(rec.date)

        for uid, data in entries_by_user.items():
            count = data["count"]
            date_range = self._date_range_label(data["dates"])
            message = (
                self.env._("%(count)d of your availability entries have been reset to draft (%(range)s).", count=count, range=date_range)
                if count > 1
                else self.env._("Your availability entry has been reset to draft (%(range)s).", range=date_range)
            )
            user = self.env["res.users"].browse(uid)
            self.env["mail.thread"].message_notify(
                body=message,
                subject="Availability entries reseted",
                partner_ids=[
                    user.partner_id.id,
                ],
            )
            self.env["bus.bus"]._sendone(
                user.partner_id,
                "simple_notification",
                {"title": self.env._("Availability reset to draft"), "message": message, "sticky": False},
            )
