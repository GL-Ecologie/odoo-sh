{
    'name': "custom_planning_module",

    'summary': "Extends base planning module to allow extra shift planinng logic.",

    'description': """
    This module extends the base planning module with the following features:
    - Shift planning takes into account employee's shift preference fields (maximum number of shifts per week, types of shift they want to work, etc.)
    """,

    'author': "Julian Ruiz Burgos",
    'website': "https://www.gl-ecologie.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Customizations',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'planning', 'project', 'hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/planning_slot_view.xml',
        'views/planning_shift_type_views.xml',
        'security/ir.model.access.csv'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

