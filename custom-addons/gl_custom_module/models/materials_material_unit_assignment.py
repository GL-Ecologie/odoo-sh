from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime, logging

class MaterialUnitAssignment(models.Model):
    
    _name = 'materials.material_unit_assignment'
    _description = 'Custom Material Unit Assignment model'

    
    material_unit_id = fields.Many2one( 
        'materials.material_unit',
        string="Material Unit"
    )

    shift_id = fields.Many2one(
        "planning.slot",
        string="Shift"
    )
    
    notes = fields.Char(
        string="Notes"
    )