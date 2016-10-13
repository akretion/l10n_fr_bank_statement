# -*- coding: utf-8 -*-
# © 2011-2016 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import datetime
from openerp.addons.account_move_base_import.parser.file_parser import (
    FileParser
)
from csv import Dialect
from _csv import QUOTE_MINIMAL, register_dialect


def format_date(val):
    return datetime.datetime.strptime(val, "%Y%m%d")


class sg_dialect(Dialect):
    """Describe the usual properties of Excel-generated CSV files."""
    delimiter = '\t'
    quotechar = '"'
    doublequote = False
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = QUOTE_MINIMAL
register_dialect("sg_dialect", sg_dialect)


def float4d(val):
    return float(val or 0.0)/10000


def float2d(val):
    return float(val or 0.0)/100


class SocieteGeneraleFileParser(FileParser):
    """
    Société Générale parser that use a define format in csv to import into a
    Account Move.
    """

    def __init__(self, journal, ftype='csv', **kwargs):
        conversion_dict = {
            u"TRANSACTION_ID": unicode,
            u"CARD_TYPE": unicode,
            u"ORDER_ID": unicode,
            u"REMITTANCE_DATE": format_date,
            u"PAYMENT_DATE": format_date,
            u"BRUT_AMOUNT": float2d,
            u"NET_AMOUNT": float4d,
            u"COMMISSION_AMOUNT": float4d,
            u"OPERATION_TYPE": unicode,
        }
        dialect = sg_dialect
        super(SocieteGeneraleFileParser, self).__init__(journal, ftype='csv',
                extra_fields=conversion_dict, dialect=dialect, **kwargs)

    @classmethod
    def parser_for(cls, parser_name):
        """
        Used by the new_bank_statement_parser class factory. Return true if
        the providen name is generic_csvxls_so
        """
        return parser_name == 'societe_generale_cb_csvparser'

    def _pre(self, *args, **kwargs):
        split_file = self.filebuffer.split("\n")
        selected_lines = ""
        for line in split_file:
            if line.startswith('ENTETE') or line.startswith('MATCHING'):
                if selected_lines:
                    selected_lines += "\n%s" % line
                else:
                    selected_lines = line
        self.filebuffer = selected_lines

    def _post(self, *args, **kwargs):
        """
        Remove pending lines
        """
        good_row_list = []
        for row in self.result_row_list:
            if not row[u'CARD_TYPE'] == "PAYPAL":
                good_row_list.append(row)
        self.result_row_list = good_row_list
        res = super(SocieteGeneraleFileParser, self)._post(*args, **kwargs)
        if self.result_row_list:
            date = self.result_row_list[0]['REMITTANCE_DATE'] or ''
            self.move_name = "CB-" + date.strftime('%y%m%d')
            self.move_date = date
        return res

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
        if line.get('OPERATION_TYPE') == 'CT':
            amount = -line["NET_AMOUNT"]
        else:
            amount = line["BRUT_AMOUNT"]
        return {
            'name': line.get(u"ORDER_ID", "/"),
            'date_maturity': line.get(u"PAYMENT_DATE",
                                      datetime.datetime.now().date()),
            'credit': amount > 0.0 and amount or 0.0,
            'debit': amount < 0.0 and -amount or 0.0,
            'transaction_ref': line.get(u"ORDER_ID", ""),
        }
