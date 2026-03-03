from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime, logging

class MaterialUnitStatus(models.Model):
    
    _name = 'materials.material_unit_status'
    _description = 'Custom Material unit status model'

    name = fields.Char(required=True)

    material_unit_ids = field.One2many(
        "materials.material_unit",
        string = "Units with this status."
    )
    
    notes = fields.Char(
        string="Notes"
    )