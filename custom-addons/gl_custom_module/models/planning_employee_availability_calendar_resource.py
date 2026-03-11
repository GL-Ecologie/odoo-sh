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
        
        if not self.env['planning.calendar.resource'].search_count([('user_id', '=', user_id), ('resource_id', '=', False)]):
            self.env['planning.calendar.resource'].create({'resource_id': False, 'user_id': user_id})
        return self.search_read(domain=[('user_id', '=', user_id)], fields=field_names)