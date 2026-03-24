from odoo import models


class ProjectTask(models.Model):
    _inherit = "project.task"
    _description = "Custom planning slot (shift) model"
    
    def action_create_shifts_for_task(self):
        """Open the multi-resource shift creation wizard pre-filled with
        this task's project and task, for manager use from the task form.
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
