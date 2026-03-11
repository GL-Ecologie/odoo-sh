from odoo import models, fields, api
from odoo.exceptions import UserError


class PlanningEmployeeAvailabilityCalendarResource(models.Model):
    _name = "planning.employee_availability_calendar_resource"
    _description = "Employee Availability Calendar Resource"

    user_id = fields.Many2one(
        "res.users",
        required=True,
        default=lambda self: self.env.user,
        ondelete="cascade",
    )

    resource_id = fields.Many2one(
        "resource.resource",
    )

    active = fields.Boolean(default=True)
    checked = fields.Boolean(default=True)

    def get_calendar_filters(self, user_id, field_names):
        user = self.env["res.users"].browse(user_id)

        if user.has_group("planning.group_planning_manager"):
            target_resources = self.env["hr.employee"].search([("active", "=", True)]).mapped("resource_id").filtered(lambda r: r)
        else:
            employee = self.env["hr.employee"].search([("user_id", "=", user_id)], limit=1)
            target_resources = employee.resource_id if employee and employee.resource_id else self.env["resource.resource"]

        existing_resource_ids = set(
            self.search([("user_id", "=", user_id)]).mapped("resource_id").ids
        )

        missing_vals = []
        for resource in target_resources:
            if resource.id not in existing_resource_ids:
                missing_vals.append({
                    "user_id": user_id,
                    "resource_id": resource.id,
                    "checked": not user.has_group("planning.group_planning_manager"),
                })

        if missing_vals:
            self.create(missing_vals)

        return self.search_read(
            domain=[("user_id", "=", user_id)],
            fields=field_names,
        )