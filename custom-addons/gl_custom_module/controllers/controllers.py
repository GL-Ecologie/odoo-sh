# from odoo import http


# class CustomPlanningModule(http.Controller):
#     @http.route('/custom_planning_module/custom_planning_module', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_planning_module/custom_planning_module/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_planning_module.listing', {
#             'root': '/custom_planning_module/custom_planning_module',
#             'objects': http.request.env['custom_planning_module.custom_planning_module'].search([]),
#         })

#     @http.route('/custom_planning_module/custom_planning_module/objects/<model("custom_planning_module.custom_planning_module"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_planning_module.object', {
#             'object': obj
#         })

