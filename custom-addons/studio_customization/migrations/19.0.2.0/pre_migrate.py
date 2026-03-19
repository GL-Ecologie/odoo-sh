from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    """
    Ensure ir.model.data entries exist for Studio fields that were created via
    the UI before they were included in this module's XML. Without these entries,
    Odoo attempts an INSERT instead of an UPDATE and fails with a duplicate key error.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    _ensure_field_linked(
        env,
        model="planning.slot",
        field_name="x_studio_reminder",
        xml_id="new_multiline_text_c_01f22bf1-7c39-4847-9ea2-821746e1fb16",
    )


def _ensure_field_linked(env, model, field_name, xml_id):
    """Link an existing ir.model.fields record to a studio_customization XML id
    so that the module upgrade performs an UPDATE rather than an INSERT."""
    field = env["ir.model.fields"].search(
        [("model", "=", model), ("name", "=", field_name)], limit=1
    )
    if not field:
        return

    existing = env["ir.model.data"].search(
        [("module", "=", "studio_customization"), ("name", "=", xml_id)], limit=1
    )
    if not existing:
        env["ir.model.data"].create(
            {
                "module": "studio_customization",
                "name": xml_id,
                "model": "ir.model.fields",
                "res_id": field.id,
                "noupdate": True,
            }
        )
