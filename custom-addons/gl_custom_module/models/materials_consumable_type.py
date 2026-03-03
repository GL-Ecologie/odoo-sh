from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime, logging

class ConsumableType(models.Model):
    
    _name = 'materials.consumable_type'
    _description = 'Custom Consumable type model'

    name = fields.Char(required=True)

    material_type_ids = fields.One2many(
        "materials.material_type",
        string="Materials that use this consumable type."
    )

    current_stock = fields.Integer()

    needed_stock = fields.Integer(
        string="Stock needed", 
        help="Dynamic needed stock calculation for this consumable type", 
        compute="_compute_needed_stock"
    )
    
    notes = fields.Char(
        string="Notes"
    )


    def _compute_needed_stock(self):
        """
        This method calculates how much stock of a certain material consumable is needed based on the total amount of units.
        """

        pass