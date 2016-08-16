# -*- coding: utf-8 -*-
# © 2016 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import logging
from openerp import models, fields, api, _
from openerp.exceptions import UserError
from openerp.addons.account_bank_statement_import_sogenactif.parser.\
    sogenactif_file_parser import SogenactifParser
import datetime
    

_logger = logging.getLogger(__name__)


class AccountBankStatementImport(models.TransientModel):
    _inherit = 'account.bank.statement.import'

    @api.multi
    def _check_sogenactif(self, data_file, journal):
        if journal and journal.sogenactif_type:
            try:
                sogen = SogenactifParser(
                    data_file, journal.sogenactif_type)
                sogen.parse()
            except:
                return False
        else:
            return False
        return sogen

    @api.model
    def _parse_file(self, data_file):
        """ Import a file in French CFONB format"""
        journal_id = self.env.context.get('journal_id', False)
        journal = self.env['account.journal'].browse(journal_id)
        sogen = self._check_sogenactif(data_file, journal)
        if not sogen:
            return super(AccountBankStatementImport, self)._parse_file(
                data_file)
        date_statement = False
        transactions = []
        for line in sogen.result_row_list:
            amount = line.get("Montant d'origine", 0.0)
            ref = line[u"Référence de la commande"]
            date_str = line.get("Date de la transaction") or \
                datetime.datetime.now().date().strftime('%Y-%m-%d')
            if not date_statement:
                date_statement = date_str
            vals_line = {
                'date': date_str,
                'name': ref,
                'ref': ref,
                'unique_import_id':
                '%s-%s' % (date_str, ref),
                'amount': amount,
                }
            transactions.append(vals_line)
        if transactions:
            vals_bank_statement = [{
                'name': _('%s %s') % (
                    sogen.type, date_statement),
                'date': date_statement,
                'transactions': transactions,
                }]
        else:
            vals_bank_statement = None
        if transactions:
            return 'EUR', None, vals_bank_statement
