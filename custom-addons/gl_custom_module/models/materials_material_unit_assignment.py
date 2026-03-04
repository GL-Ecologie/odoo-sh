from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime, logging

class MaterialUnitAssignment(models.Model):
    
    _name = 'materials.material_unit_assignment'
    _description = 'Custom Material Unit Assignment model'

    _logger = logging.getLogger(__name__)
    
    material_unit_id = fields.Many2one( 
        'materials.material_unit',
        string="Material Unit",
        required=True
    )

    shift_id = fields.Many2one(
        "planning.slot",
        string="Shift",
        required=True
    )
    
    notes = fields.Char(
        string="Notes"
    )

    @api.constrains("material_unit_id", "shift_id")
    def _check_unit_not_double_booked(self):
        self._logger.info("Entering _check_unit_not_double_booked")
        for rec in self:
            if not rec.material_unit_id or not rec.shift_id:
                self._logger.info("Fields not field, skipping...")
                continue

            # adjust these field names if your planning.slot uses different ones
            start = rec.shift_id.start_datetime.date()
            end = rec.shift_id.end_datetime.date()
            self._logger.info(f"Time window: From {start} to {end}")
            if not start or not end:
                self._logger.info("No start or end date set, skipping...")
                continue

            # resource/person assigned to the shift (planning.slot uses resource_id)
            rec_resource = rec.shift_id.resource_id

            # Find other assignments for same unit where shifts overlap
            domain = [
                ("id", "!=", rec.id),
                ("material_unit_id", "=", rec.material_unit_id.id),
                ("shift_id.start_datetime", "<=", end),
                ("shift_id.end_datetime", ">=", start),
            ]
            others = self.search(domain)

            self._logger.info(f"Results of domain search:\n Other shifts found: {len(others)}")

            # Allow overlap only if the resource/person is the same
            conflicts = others.filtered(
                lambda a: a.shift_id.resource_id != rec_resource
            )

            self._logger.info(f"# Conflicts: {len(conflicts)}")

            
            
            if conflicts:
                raise ValidationError(_(
                    f"This material unit is already assigned to another overlapping shift (from {start} to {end}) "
                    f"for a different person ({[conflict.shift_id.resource_id.name for conflict in conflicts]})"
                ))