from odoo import models, fields, api, _


class PlanningSlot(models.Model):
    _inherit = "planning.slot"
    
    _name = 'planning.slot'
    _description = 'Custom planning slot'