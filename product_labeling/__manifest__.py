{
    'name': "Маркировка товара",
    'summary': "Маркировка, учёт и отслеживание товара",
    'description': """
Информационная система "Маркировка товара" предназначена для того, чтобы оперативно получить информацию о месте нахождения товара и его себестоимости в любой момент времени.
    """,
    'author': "pinocoladium",
    'website': "https://github.com/pinocoladium",
    'category': 'Operations',
    'version': '0.1',
    'depends': ['base'],
    'data': [
        'views/views.xml',
        'views/templates.xml',
        'security/ir.model.access.csv'
    ],
    'application': True,
}

