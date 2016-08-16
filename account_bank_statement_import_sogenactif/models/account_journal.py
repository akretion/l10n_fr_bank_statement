# -*- coding: utf-8 -*-
# © 2016 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openerp import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    sogenactif_type = fields.Selection(
        [('paypal', 'Paypal'), ('amex', 'Amex')])


