from odoo import models, fields

class PlanningShiftType(models.Model):
    _name = 'planning.shift_type'
    _description = 'Shift Type'

    name = fields.Char(required=True)
    time_of_day = fields.Selection(
        [
            ("morning", "Morning"),
            ("afternoon", "Afternoon"),
            ("evening", "Evening"),
            ("night", "Night"),
        ],
        string="Time of Day",
        required=True,
        help="Technical classification used by scheduling logic (e.g. evening/morning conflict detection). Always set in English regardless of shift name language.",
    )
    # TODO: Add i18n/nl.po translation file to the module so custom field labels
    # (e.g. "Time of Day", "Max shifts per week") and selection option labels
    # ("Morning", "Evening", etc.) are shown in Dutch when the UI language is set to NL.
    # Steps: run `odoo-bin --i18n-export`, fill in translations, place under i18n/nl.po.