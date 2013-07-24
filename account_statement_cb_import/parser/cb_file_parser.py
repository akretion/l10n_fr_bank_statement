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

class cb_dialect(Dialect):
    """Describe the usual properties of Excel-generated CSV files."""
    delimiter = '\t'
    quotechar = '"'
    doublequote = False
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = QUOTE_MINIMAL
register_dialect("cb_dialect", cb_dialect)

def float4d(val):
    return float(val or 0.0)/10000

def float2d(val):
    return float(val or 0.0)/100


class CBFileParser(FileParser):
    """
    Standard parser that use a define format in csv or xls to import into a
    bank statement. This is mostely an example of how to proceed to create a new
    parser, but will also be useful as it allow to import a basic flat file.
    """

    def __init__(self, parse_name, ftype='csv'):
        conversion_dict = {
            u"TRANSACTION_ID": unicode,
            u"CARD_TYPE": unicode,
            u"ORDER_ID": unicode,
            u"REMITTANCE_DATE": {
                'type': datetime.datetime,
                'format': "%Y%m%d",
            },
            u"BRUT_AMOUNT": float2d,
            u"NET_AMOUNT": float4d,
            u"COMMISSION_AMOUNT": float4d,
            u"OPERATION_TYPE":unicode,
        }
        #TODO FIXME
        header = [
            u"ENTETE",u"MERCHANT_COUNTRY",u"MERCHANT_ID",u"CONTRACT",u"PAYMENT_DATE",u"TRANSACTION_ID",u"ORIGIN_AMOUNT",u"CURRENCY_CODE",u"CARD_TYPE",u"ORDER_ID",u"RETURN_CONTEXT",u"CUSTOMER_ID",u"OPERATION_TYPE",u"OPERATION_NUMBER",u"REMITTANCE_DATE",u"REMITTANCE_TIME",u"BRUT_AMOUNT",u"MATCH_STATUS",u"REMITTANCE_NB",u"NET_AMOUNT",u"COMMISSION_AMOUNT",u"COMMISSION_CURRENCY"
            ]
        dialect=cb_dialect
        super(CBFileParser,self).__init__(parse_name, ftype='csv',
                                              conversion_dict=conversion_dict,
                                              dialect=dialect)

    @classmethod
    def parser_for(cls, parser_name):
        """
        Used by the new_bank_statement_parser class factory. Return true if
        the providen name is generic_csvxls_so
        """
        return parser_name == 'cb_csvparser'

    #def _custom_format(self, *args, **kwargs):
    #    self.filebuffer = self.filebuffer.decode('iso-8859-15')
    #    #remove non-bracking space
    #    self.filebuffer = self.filebuffer.replace(u'\xa0', u' ')
    #    #encode in utf-8
    #    self.filebuffer = self.filebuffer.encode('utf-8')

    def _pre(self, *args, **kwargs):
        split_file = self.filebuffer.split("\n")
        selected_lines = ""
        for line in split_file:
            if line.startswith('ENTETE') or line.startswith('MATCHING'):
                if selected_lines:
                   selected_lines += "\n%s"%line
                else:
                    selected_lines = line
        self.filebuffer = selected_lines

    def _parse(self, *args, **kwargs):
        context = kwargs['context']
        self.statement_name = context.get('file_name').replace('rapprochement_', '').replace('.xls', '')
        return super(CBFileParser, self)._parse(*args, **kwargs)


    def _post(self, *args, **kwargs):
        """
        Remove pending lines
        """
        good_row_list = []
        total_received = 0
        total_paid = 0
        total = defaultdict(lambda : defaultdict(float))
        #TODO use new system with statement transfers!
        for row in self.result_row_list:
            if not row[u'CARD_TYPE'] == "PAYPAL":
                good_row_list.append(row)
                if row['OPERATION_TYPE'] == 'CT':
                    row['NET_AMOUNT'] = - float(row['NET_AMOUNT'])
                    total[row['REMITTANCE_TIME']]['total_paid'] += row['NET_AMOUNT']/100.
                else:
                    total[row['REMITTANCE_TIME']]['total_received'] += float(row['BRUT_AMOUNT'])
        self.result_row_list = good_row_list
        for date in total:
            for key, amount in total[date].iteritems():
                if amount:
                    self.result_row_list.append({
                        'TRANSACTION_ID': 'bank_transfer',
                        'ORDER_ID': _('Bank Transfer'),
                        'type': 'Bank Transfer',
                        'REMITTANCE_DATE': self.result_row_list[0]['REMITTANCE_DATE'],
                        'BRUT_AMOUNT': - amount,
                        'NET_AMOUNT':0,
                        'CARD_TYPE': 'VIR',
                        'COMMISSION_AMOUNT': 0,
                        'OPERATION_TYPE': '',
                        })
        return super(CBFileParser, self)._post(*args, **kwargs)

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
        if line.get('OPERATION_TYPE') == 'CT':
            amount = line["NET_AMOUNT"]
        else:
            amount = line["BRUT_AMOUNT"]
        res = {
            'name': line.get(u"TRANSACTION_ID", "/"),
            'date': line.get(u"REMITTANCE_DATE", datetime.datetime.now().date()),
            'amount': amount,
            'ref': line.get(u"ORDER_ID", "/"),
            'commission_amount': line["COMMISSION_AMOUNT"],
        }
        return res
