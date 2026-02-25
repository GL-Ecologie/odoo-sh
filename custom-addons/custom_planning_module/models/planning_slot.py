from odoo import models, fields, api


class PlanningSlot(models.Model):
    _inherit = "planning.slot"
    
    _name = 'custom_planning_module.PlanningSlot'
    _description = 'custom_planning_module.PlanningSlot'