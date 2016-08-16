# -*- coding: utf-8 -*-
# © 2011-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    import_type = fields.Selection(
        selection_add=[
            ('banque_accord_txtparser',
             'Banque Accord .txt'),
        ])
