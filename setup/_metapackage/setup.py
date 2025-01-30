import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-akretion-l10n_fr_bank_statement",
    description="Meta package for akretion-l10n_fr_bank_statement Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-account_bank_statement_import_sogenactif',
        'odoo9-addon-account_move_banque_accord_import',
        'odoo9-addon-account_move_be2bill_import',
        'odoo9-addon-account_move_cb_societe_generale_import',
        'odoo9-addon-account_move_sogenactif_import',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 9.0',
    ]
)
