# -*- coding: utf-8 -*-
###############################################################################
#
#   account_statement_cic_import for OpenERP
#   Authors: Sebastien Beau <sebastien.beau@akretion.com>
#            Benoît Guillot <benoit.guillot@akretion.com>
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
from account_statement_base_import.parser.file_parser import FileParser


class CICFileParser(FileParser):
    """
    Standard parser that use a define format in csv or xls to import into a
    bank statement. This is mostely an example of how to proceed to create a new
    parser, but will also be useful as it allow to import a basic flat file.
    """

    def __init__(self, parse_name, ftype='csv'):
        conversion_dict = {
            u"Date de valeur": {
                'type': datetime.datetime,
                'format': "%d/%m/%Y",
            },
            u"Débit": float,
            u"Crédit": float,
            u"Libellé": unicode,
        }
        #TODO FIXME
        header = [
            "Date d'opération",u"Date de valeur",u"Débit",u"Crédit",u"Libellé",u"Solde"
                ]
        super(CICFileParser,self).__init__(parse_name, ftype=ftype,
                                              conversion_dict=conversion_dict)

    @classmethod
    def parser_for(cls, parser_name):
        """
        Used by the new_bank_statement_parser class factory. Return true if
        the providen name is generic_csvxls_so
        """
        return parser_name == 'cic_csvparser'

    def _custom_format(self, *args, **kwargs):
        self.filebuffer = self.filebuffer.decode('iso-8859-15')
        #remove non-bracking space
        self.filebuffer = self.filebuffer.replace(u'\xa0', u' ')
        #encode in utf-8
        self.filebuffer = self.filebuffer.encode('utf-8')


    def get_st_line_vals(self, line, *args, **kwargs):
        """
        This method must return a dict of vals that can be passed to create
        method of statement line in order to record it. It is the responsibility
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
                    'label':value,
                    'commission_amount':value,
                }
        In this generic parser, the commission is given for every line, so we store it
        for each one.
        """
        amount = -line[u"Débit"] or line[u"Crédit"] or 0.0

        res = {
            'name': line.get(u"Libellé", "/"),
            'date': line.get(u"Date de valeur", datetime.datetime.now().date()),
            'amount': amount,
            'label': line.get(u"Libellé", "/"),
            'ref': "/",

        }
        return res
