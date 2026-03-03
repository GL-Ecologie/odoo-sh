from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime, logging

class MaterialCategory(models.Model):
    
    _name = 'materials.material_category'
    _description = 'Custom Material category model'

    name = fields.Char(required=True)
    
    material_type_ids = fields.One2many( 
        'materials.material_type',
        "material_category_id",
        string="Materials"
    )

    notes = fields.Char(
        string="Notes"
    )