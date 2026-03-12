from odoo import models, fields, api
from odoo.exceptions import UserError
import json


class PlanningEmployeeAvailabilityBatchEditWizard(models.TransientModel):
    _name = "planning.employee_availability_batch_edit_wizard"
    _description = "Batch Edit Employee Availability"

    entry_ids = fields.Many2many(
        "planning.employee_availability_entry",
        relation="planning_employee_availability_batch_edit_2_entry",
        string="Availability Entries",
    )

    shift_type_id = fields.Many2one(
        "planning.shift_type",
    )

    available = fields.Boolean()

    set_shift_type = fields.Boolean(string="Update shift type")
    set_available = fields.Boolean(string="Update availability")

    @api.model
    def action_open_wizard(self):
        active_ids = self.env.context.get("active_ids", [])
        if not active_ids:
            raise UserError(self.env._("No availability entries were selected."))

        return {
            "type": "ir.actions.act_window",
            "name": _("Batch Edit Availability"),
            "res_model": "planning.employee_availability_batch_edit_wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_entry_ids": [(6, 0, active_ids)],
            },
        }

    def action_apply(self):
        self.ensure_one()

        if not self.entry_ids:
            raise UserError(self.env._("No availability entries were selected."))

        vals = {}

        if self.set_shift_type:
            vals["shift_type_id"] = self.shift_type_id.id

        if self.set_available:
            vals["available"] = self.available

        if not vals:
            raise UserError(self.env._("No changes were selected."))

        self.entry_ids.write(vals)

        self.entry_ids.action_request_validation()

        return {"type": "ir.actions.act_window_close"}
