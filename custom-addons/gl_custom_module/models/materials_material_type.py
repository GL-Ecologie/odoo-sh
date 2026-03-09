from odoo import models, fields


class MaterialType(models.Model):

    _name = "materials.material_type"
    _description = "Custom Material type model"

    name = fields.Char(required=True)
    material_category_id = fields.Many2one("materials.material_category", string="Material Category")

    material_unit_ids = fields.One2many("materials.material_unit", "material_type_id", string="List of material units")

    booked_quantity = fields.Integer(string="Units booked", help="Dynamic booked quantity calculation for this material type")

    available_quantity = fields.Integer(
        string="Units available", help="Dynamic available quantity calculation for this material type", compute="_compute_units_available"
    )

    consumable_type_id = fields.Many2one("materials.consumable_type", string="Uses consumable")

    consumable_quantity = fields.Integer()

    notes = fields.Char()

    def _compute_units_available(self):
        """
        Calculate how many units of this specific material type are currently available.
        """
        for material_type in self:
            material_type.available_quantity = len(material_type.material_unit_ids) - material_type.booked_quantity
