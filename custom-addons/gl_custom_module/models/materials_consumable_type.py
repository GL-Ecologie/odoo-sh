from odoo import models, fields


class ConsumableType(models.Model):

    _name = "materials.consumable_type"
    _description = "Custom Consumable type model"

    name = fields.Char(required=True)

    material_type_ids = fields.One2many("materials.material_type", "consumable_type_id", string="Materials that use this consumable type.")

    current_stock = fields.Integer()

    needed_stock = fields.Integer(
        string="Stock needed",
        help="Dynamic needed stock calculation for this consumable type",
    )

    notes = fields.Char()

