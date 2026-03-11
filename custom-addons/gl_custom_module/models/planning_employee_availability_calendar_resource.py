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
        is_manager = user.has_group("planning.group_planning_manager")

        if is_manager:
            resources = self.env["hr.employee"].search([]).mapped("resource_id")
        else:
            employee = self.env["hr.employee"].search([("user_id", "=", user_id)], limit=1)
            resources = employee.resource_id

        existing_resource_ids = self.search([
            ("user_id", "=", user_id),
        ]).mapped("resource_id").ids

        missing_resources = resources.filtered(lambda r: r.id not in existing_resource_ids)

        for resource in missing_resources:
            self.create({
                "user_id": user_id,
                "resource_id": resource.id,
                "checked": True if not is_manager else False,
            })

        return self.search_read(
            domain=[("user_id", "=", user_id)],
            fields=field_names,
        )