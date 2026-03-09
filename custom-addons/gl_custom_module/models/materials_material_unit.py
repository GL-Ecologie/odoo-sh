from odoo import models, fields

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

    serial_number = fields.Char(
        string="Serial number",
        help="Serial number of this unit?",
    )

    rental = fields.Boolean(
        string="Is rental",
        help="Is this a rental unit?",
    )

    notes = fields.Char()