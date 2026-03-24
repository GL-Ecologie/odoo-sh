{
    'name': "GL-Ecologie Customizations",

    'summary': "Extends the Odoo models to incorporate features custom for GL-Ecologie",

    'description': """
    This module extends the base planning module with the following features:
    - Public employees can change some parameters, like max shifts per week, etc.
    - Shift planning takes into account employee's shift preference fields (maximum number of shifts per week, types of shift they want to work, etc.)
    """,
    'license': 'LGPL-3',
    'author': "Julian Ruiz Burgos",
    'website': "https://www.gl-ecologie.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Customizations',
    'version': '1.1.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'planning', 'project', 'hr'],

    # always loaded
    'data': [
        'security/security.xml',
        'data/mail_templates.xml',
        'security/ir.model.access.csv',
        'views/planning_slot_views.xml',
        'views/planning_shift_type_views.xml',
        'views/planning_employee_availability_views.xml',
        'views/planning_employee_availability_batch_edit_wizard_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_employee_public_views.xml',
        'views/materials_consumable_type_views.xml',
        'views/materials_material_category_views.xml',
        'views/materials_material_type_views.xml',
        'views/materials_material_unit_views.xml',
        'views/materials_menu_views.xml',
        'views/planning_multi_assign_wizard_views.xml',
    ],
    "assets": {
        "web.assets_backend": [
            "gl_custom_module/static/src/views/employee_availability_calendar/employee_availability_calendar_view.js",
            "gl_custom_module/static/src/views/employee_availability_calendar/employee_availability_calendar.xml",
            "gl_custom_module/static/src/scss/employee_availability_calendar.scss",
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

