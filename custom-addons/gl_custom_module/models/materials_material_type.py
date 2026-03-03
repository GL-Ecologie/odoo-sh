from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime, logging

class MaterialType(models.Model):
    
    _name = 'materials.material_type'
    _description = 'Custom Material type model'

    name = fields.Char(required=True)
    material_category_id = fields.Manytoone( 
        'materials.material_category',
        string="Material Category"
    )

    material_unit_ids = fields.Onetomany(
        "materials.material_unit",
        string="List of material units"
    )

    booked_quantity = fields.Integer(
        string="Units booked", 
        help="Dynamic booked quantity calculation for this material type", 
        compute="_compute_units_already_booked"
    )

    available_quantity = fields.Integer(
        string="Units available",
        help="Dynamic available quantity calculation for this material type",
        compute="_compute_units_available"
    )

    consumable_type_id = fields.Manytoone(
        "materials.consumable_type",
        string="Type of consumable (if any) needed"
    )

    consumable_quantity = fields.Integer()

    notes = fields.Char(
        string="Notes"
    )

    def __compute_units_already_booked(self):
        """
        Calculates how many units of this specific material type are currently booked.
        """
        pass

    def _compute_units_available(self):
        """
        Calculate how many units of this specific material type are currently available.
        """
        pass