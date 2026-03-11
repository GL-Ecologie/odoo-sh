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
        employee = self.env["hr.employee"].search([("user_id", "=", user.id)], limit=1)
        resource = employee.resource_id if employee else False

        if resource and not self.search_count([
            ("user_id", "=", user_id),
            ("resource_id", "=", resource.id),
        ]):
            self.create({
                "user_id": user_id,
                "resource_id": resource.id,
                "checked": True,
            })

        return self.search_read(
            domain=[("user_id", "=", user_id)],
            fields=field_names,
        )