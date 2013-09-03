# -*- coding: utf-8 -*-
###############################################################################
#
#   account_statement_cb_import for OpenERP
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
from csv import Dialect
from _csv import QUOTE_MINIMAL, register_dialect
from collections import defaultdict
import datetime

class sogenactif_dialect(Dialect):
    """Describe the usual properties of Excel-generated CSV files."""
    delimiter = '\t'
    quotechar = '"'
    doublequote = False
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = QUOTE_MINIMAL
register_dialect("sogenactif_dialect", sogenactif_dialect)

def float_or_zero(val):
    return float(val.replace(',', '.')) if val else 0.0

def format_date(val):
    return datetime.datetime.strptime(val.split(' ')[0], "%d/%m/%Y")


class SogenactifFileParser(FileParser):
    """
    Standard parser that use a define format in csv or xls to import into a
    bank statement. This is mostely an example of how to proceed to create a new
    parser, but will also be useful as it allow to import a basic flat file.
    """

    def __init__(self, parse_name, ftype='csv'):
        conversion_dict = {
            u"Date de la transaction": format_date,
            u"Référence de la commande": unicode,
            u"Montant d'origine": float_or_zero,
            u"Type de carte": unicode,
            u"Etat de la transaction": unicode,
        }
        dialect=sogenactif_dialect
        super(SogenactifFileParser,self).__init__(parse_name, ftype='csv',
                                              conversion_dict=conversion_dict,
                                              dialect=dialect)

    def _custom_format(self, *args, **kwargs):
        self.filebuffer = self.filebuffer.decode('iso-8859-15').encode('utf-8')
        self.filebuffer = self.filebuffer.replace('="', '').replace('"', '')
        return True

    def _post(self, *args, **kwargs):
        """
        Remove pending lines
        """
        super(SogenactifFileParser, self)._post(*args, **kwargs)
        res = []
        for row in self.result_row_list:
            if row["Type de carte"] == self._card_type\
                    and row["Etat de la transaction"] != "refusée":
                res.append(row)
        self.result_row_list = res
        return True

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
        ref = line[u"Référence de la commande"]
        if not ref[0:3] == "DEV":
            ref = "DEV-%s"%ref

        res = {
            'name': ref,
            'date': line.get("Date de la transaction"),
            'amount': line["Montant d'origine"],
            'ref': ref,
            'commission_amount': 0,
        }
        return res


class PaypalSogenactifFileParser(SogenactifFileParser):
    _card_type = "PAYPAL"

    @classmethod
    def parser_for(cls, parser_name):
        """
        Used by the new_bank_statement_parser class factory. Return true if
        the providen name is generic_csvxls_so
        """
        return parser_name == 'sogenactif_paypal_csvparser'


class AmericanSogenactifFileParser(SogenactifFileParser):
    _card_type = "AMEX"

    @classmethod
    def parser_for(cls, parser_name):
        """
        Used by the new_bank_statement_parser class factory. Return true if
        the providen name is generic_csvxls_so
        """
        return parser_name == 'sogenactif_american_csvparser'
