# -*- coding: utf-8 -*-
###############################################################################
#
#   account_statement_paypal_import for OpenERP
#   Authors: Sebastien Beau <sebastien.beau@akretion.com>
#   Copyright 2013 Akretion
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.tools.translate import _
import datetime
from account_statement_base_import.parser.parser import BankStatementImportParser
from cfonb.parser.statement import Statement
import tempfile


class CFONBFileParser(BankStatementImportParser):
    """
    Standard parser that use a define format in csv or xls to import into a
    bank statement. This is mostely an example of how to proceed to create a new
    parser, but will also be useful as it allow to import a basic flat file.
    """

    @classmethod
    def parser_for(cls, parser_name):
        """
        Used by the new_bank_statement_parser class factory. Return true if
        the providen name is generic_csvxls_so
        """
        return parser_name == 'cfonb_parser'

    def _custom_format(self, *args, **kwargs):
        """
        Implement a method in your parser to convert format, encoding and so on before
        starting to work on datas. Work on self.filebuffer
        """
        return True

    def _pre(self, *args, **kwargs):
        """
        Implement a method in your parser to make a pre-treatment on datas before parsing
        them, like concatenate stuff, and so... Work on self.filebuffer
        """
        self.filebuffer = self.filebuffer.replace('\r\n', '\n').replace('\r', '\n')
        return True

    def _parse(self, *args, **kwargs):
        """
        Implement a method in your parser to save the result of parsing self.filebuffer
        in self.result_row_list instance property.
        """
        wb_file = tempfile.NamedTemporaryFile()
        wb_file.write(self.filebuffer)
        wb_file.seek(0)
        statement = Statement()
        statement.parse(wb_file)
        self.result_row_list = statement.lines
        self.balance_start = statement.header.prev_amount
        self.balance_end = statement.footer.next_amount
        return True

    def _validate(self, *args, **kwargs):
        """
        Implement a method in your parser  to validate the self.result_row_list instance
        property and raise an error if not valid.
        """
        return True

    def _post(self, *args, **kwargs):
        """
        Implement a method in your parser to make some last changes on the result of parsing
        the datas, like converting dates, computing commission, ...
        Work on self.result_row_list and put the commission global amount if any
        in the self.commission_global_amount one.
        """
        return True

    def get_st_line_vals(self, line, *args, **kwargs):
        """
        Implement a method in your parser that must return a dict of vals that can be
        passed to create method of statement line in order to record it. It is the responsibility
        of every parser to give this dict of vals, so each one can implement his
        own way of recording the lines.
            :param:  line: a dict of vals that represent a line of result_row_list
            :return: dict of values to give to the create method of statement line,
                     it MUST contain at least:
                {
                    'name':value,
                    'date':value,
                    'amount':value,
                    'ref':value,
                }
        """
        return {
            'name': line.get('label'),
            'date': line.get('value_date'),
            'amount': line.get('amount'),
            'ref': line.get('reference'),
        }

