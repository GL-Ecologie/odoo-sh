from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime, logging

class MaterialType(models.Model):
    
    _name = 'materials.material_type'
    _description = 'Custom Material type model'

    name = fields.Char(required=True)
    material_category_id = fields.Many2one( 
        'materials.material_category',
        string="Material Category"
    )

    material_unit_ids = fields.One2many(
        "materials.material_unit",
        "material_type_id",
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

    consumable_type_id = fields.Many2one(
        "materials.consumable_type",
        string="Uses consumable"
    )

    consumable_quantity = fields.Integer()

    notes = fields.Char(
        string="Notes"
    )

    @api.depends('material_unit_ids.material_unit_assignment_ids.shift_id.start_datetime')
    def _compute_units_already_booked(self):
        today = fields.Datetime.now()
    
        for material_type in self:
            units = material_type.material_unit_ids.filtered(
                lambda unit: any(
                    assignment.shift_id
                    and assignment.shift_id.start_datetime
                    and assignment.shift_id.start_datetime >= today
                    for assignment in unit.material_unit_assignment_ids
                )
            )
    
            self.booked_quantity = len(units)
        

    def _compute_units_available(self):
        """
        Calculate how many units of this specific material type are currently available.
        """
        self.available_quantity = len(self.material_unit_ids) - self.booked_quantity