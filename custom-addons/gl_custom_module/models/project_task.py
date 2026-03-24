from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    planning_shift_count = fields.Integer(
        string="Shifts",
        compute="_compute_planning_shift_count",
    )

    @api.depends_context("uid")
    def _compute_planning_shift_count(self):
        for task in self:
            task.planning_shift_count = self.env["planning.slot"].search_count(
                [("task_id", "=", task.id)]
            )

    def action_create_shifts_for_task(self):
        """Open the multi-resource shift creation wizard pre-filled with
        this task's project and task.
        """
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Create Shifts for Task",
            "res_model": "planning.multi_assign_wizard",
            "view_mode": "form",
            "views": [[False, "form"]],
            "target": "new",
            "context": {
                "default_mode": "create",
                "default_project_id": self.project_id.id if self.project_id else False,
                "default_task_id": self.id,
            },
        }

    def action_edit_shifts_for_task(self):
        """Open the multi-resource shift edit wizard pre-loaded with all
        shifts currently assigned to this task.
        """
        self.ensure_one()
        shift_ids = self.env["planning.slot"].search(
            [("task_id", "=", self.id)]
        ).ids
        return self.env["planning.multi_assign_wizard"].with_context(
            active_ids=shift_ids
        ).action_open_edit_wizard()
