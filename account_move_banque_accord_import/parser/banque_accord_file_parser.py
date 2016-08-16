# -*- coding: utf-8 -*-
# © 2011-2016 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import datetime
from openerp.addons.account_move_base_import.parser.parser import (
    AccountMoveImportParser
)


class BanqueAccordFileParser(AccountMoveImportParser):
    """
    Banque Accord parser that use a define format in csv to import into a
    Account Move.
    """

    def __init__(self, journal, **kwargs):
        super(BanqueAccordFileParser, self).__init__(journal, **kwargs)

    @classmethod
    def parser_for(cls, parser_name):
        return parser_name == 'banque_accord_txtparser'

    def parse_cb_financement(self, cb_transaction_lines):
        res = []
        for line in cb_transaction_lines:
            vals = {
                'transaction_id': line[313:319],
                'date': line[65:73],
                'order': '%s-%s' % (line[304:307], line[307:313]),
                'amount': float('%s.%s' % (line[223:232], line[232:237])),
                'amount_type': line[237:238],
            }
            res.append(vals)
        return res

    def parse_cb_acquisition(self, cb_transaction_lines):
        res = []
        for line in cb_transaction_lines:
            vals = {
                'transaction_id': line[234:240],
                'date': line[67:75],
                'order': '%s-%s' % (line[225:228], line[228:234]),
                'amount': float('%s.%s' % (line[187:196], line[196:201])),
                'amount_type': line[201:202],
            }
            res.append(vals)
        return res

    def parse_banque_accord_file(self, file_lines):
        banque_accord_statements = []
        cb_transaction_lines = [line for line in file_lines if line[0:4] == '0041']
        transaction_dict_list = self.parse_cb_acquisition(cb_transaction_lines)
        if transaction_dict_list:
            banque_accord_statements = transaction_dict_list

        cb_financement_lines = [line for line in file_lines if line[0:4] == '0011']
        financement_dict_list = self.parse_cb_financement(cb_financement_lines)
        if financement_dict_list:
            banque_accord_statements = financement_dict_list
        return banque_accord_statements

    def _pre(self, *args, **kwargs):
        """
        Implement a method in your parser to make a pre-treatment on datas before parsing
        them, like concatenate stuff, and so... Work on self.filebuffer
        """
        self.filebuffer = self.filebuffer.replace('\r\n', '\n').replace('\r', '\n')
#        wb_file = tempfile.NamedTemporaryFile()
#        wb_file.write(self.filebuffer)
#        wb_file.seek(0)

#        if file_lines[0][0:4] == '0000':
#            self.statement_date = file_lines[0][86:94] or ''
        return True

    def _parse(self, *args, **kwargs):
        """
        Implement a method in your parser to save the result of parsing self.filebuffer
        in self.result_row_list instance property.
        """
        file_lines = self.filebuffer.split('\n')
        self.result_row_list = self.parse_banque_accord_file(file_lines)
        if file_lines[0][0:4] == '0000':
            self.move_date = file_lines[0][86:94] or None
        return True

    def get_move_line_vals(self, line, *args, **kwargs):
        """
        This method must return a dict of vals that can be passed to create
        method of statement line in order to record it. It is the
        responsibility of every parser to give this dict of vals, so each one
        can implement his own way of recording the lines.
            :param:  line: a dict of vals that represent a line of
              result_row_list
            :return: dict of values to give to the create method of statement
              line, it MUST contain at least:
                {
                    'name':value,
                    'date_maturity':value,
                    'credit':value,
                    'debit':value
                }
        """
        if line.get('amount_type', False) == '-':
            amount = -line.get('amount', 0.0)
        else:
            amount = line.get('amount', 0.0)
        return {
            'name': line.get('order', '/') or '/',
            'date_maturity': line.get('date', datetime.datetime.now().date()),
            'credit': amount > 0.0 and amount or 0.0,
            'debit': amount < 0.0 and -amount or 0.0,
            'transaction_ref': line.get('transaction_id', ''),
        }

    def _post(self, *args, **kwargs):
        dates = []
        if not self.move_date:
            for row in self.result_row_list:
                dates.append(row['date']) 
            if dates:    
                self.move_date = max(dates)
