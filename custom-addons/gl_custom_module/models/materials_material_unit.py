from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime, logging

class MaterialUnit(models.Model):
    
    _name = 'materials.material_unit'
    _description = 'Custom Material Unit model'

    name = fields.Char(required=True)
    material_type_id = fields.Many2one( 
        'materials.material_type',
        string="Material type"
    )

    material_status_id = fields.Many2one(
        "materials.material_unit_status",
        string="Material status"
    )

    material_unit_assignment_ids = fields.One2many(
        "materials.material_unit_assignment",
        "material_unit_id",
        string="Shifts assigned to this unit"
    )
    
    serial_number = fields.Char()

    rental = fields.Binary()

    active = fields.Binary()
    
    notes = fields.Char(
        string="Notes"
    )