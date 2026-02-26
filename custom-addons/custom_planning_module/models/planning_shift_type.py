from odoo import models, fields

class PlanningShiftType(models.Model):
    _name = 'planning.shift.type'
    _description = 'Shift Type'

    name = fields.Char(required=True)
    code = fields.Char(required=True)  # e.g. 'morning', 'afternoon', etc.
    # you can add color, description, whatever later