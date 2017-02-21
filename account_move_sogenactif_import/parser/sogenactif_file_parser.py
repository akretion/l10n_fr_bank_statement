# -*- coding: utf-8 -*-
# © 2011-2016 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import datetime
from csv import Dialect
from _csv import QUOTE_MINIMAL, register_dialect
from openerp.addons.account_move_base_import.parser.file_parser import (
    FileParser
)

class sogenactif_dialect(Dialect):
    """Describe the usual properties of Excel-generated CSV files."""
    delimiter = '\t'
    quotechar = '"'
    doublequote = False
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = QUOTE_MINIMAL
register_dialect("sogenactif_dialect", sogenactif_dialect)

def format_date(val):
    return datetime.datetime.strptime(val.split(' ')[0], "%d/%m/%Y")

def float_or_zero(val):
    return float(val.replace(',', '.')) if val else 0.0


class SogenactifFileParser(FileParser):
    """Sogenactif parser that use a define format in csv or xls to import into a
    account move. This is mostely an example of how to proceed to create a
    new parser, but will also be useful as it allow to import a basic flat
    file.
    """

    def __init__(self, journal, ftype='csv', **kwargs):
        conversion_dict = {
            u"Date de la transaction": format_date,
            u"Référence de la commande": unicode,
            u"Montant d'origine": float_or_zero,
            u"Type de carte": unicode,
            u"Etat de la transaction": unicode,
        }
        dialect = sogenactif_dialect
        super(SogenactifFileParser, self).__init__(
            journal, ftype=ftype,
            extra_fields=conversion_dict,
            dialect=dialect,
            **kwargs)
        self.support_multi_moves = True
        self._moves = None

    def _custom_format(self, *args, **kwargs):
        self.filebuffer = self.filebuffer.decode('iso-8859-15').encode('utf-8')
        self.filebuffer = self.filebuffer.replace('="', '').replace('"', '')
        return True

    def _pre(self, *args, **kwargs):
        # We have to parse the file in _pre method so we can loop on the
        # result on _parse method and create multi moves
        res = self._parse_csv()
        self._moves = []
        for row in res:
            if row["Type de carte"] == self._card_type\
                    and row["Etat de la transaction"] not in (u"refusée", u"Refusée", u"refusé", u"Refusé"):
                self._moves.append(row)  
        if self._moves:
            self.move_date = format_date(self._moves[0]['Date de la transaction'])
        return True

    def _parse(self, *args, **kwargs):
        """
        Implement a method in your parser to save the result of parsing self.filebuffer
        in self.result_row_list instance property.
        """
        if self._moves:
            move = self._moves.pop(0)
            self.result_row_list = [move]
            return True
        else:
            return False

    def get_move_line_vals(self, line, *args, **kwargs):
        """
        This method must return a dict of vals that can be passed to create
        method of account move line in order to record it. It is the
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
        ref = line[u"Référence de la commande"]
        amount = line.get("Montant d'origine", 0.0)
        return {
            'name': ref,
            'date_maturity': line.get("Date de la transaction",
                                      datetime.datetime.now().date()),
            'credit': amount > 0.0 and amount or 0.0,
            'debit': amount < 0.0 and amount or 0.0,
            'transaction_ref': ref,
        }

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
