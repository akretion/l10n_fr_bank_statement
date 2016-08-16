# -*- coding: utf-8 -*-
# © 2011-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import logging
import datetime
from csv import Dialect
import csv
from _csv import QUOTE_MINIMAL, register_dialect
from openerp import models, fields, api, _
from openerp.exceptions import UserError
import tempfile

_logger = logging.getLogger(__name__)




def UnicodeDictReader(utf8_data, **kwargs):
    sniffer = csv.Sniffer()
    pos = utf8_data.tell()
    sample_data = utf8_data.read(2048)
    utf8_data.seek(pos)
    csv_reader = csv.DictReader(utf8_data, dialect=sogenactif_dialect, **kwargs)
    for row in csv_reader:
        yield dict([(unicode(key or '', 'utf-8'),
                     unicode(value or '', 'utf-8'))
                    for key, value in row.iteritems()])


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



class SogenactifParser(object):

    def __init__(self, datas, sogen_type):
        self.conversion_dict = {
            u"Date de la transaction": format_date,
            u"Référence de la commande": unicode,
            u"Montant d'origine": float_or_zero,
            u"Type de carte": unicode,
            u"Etat de la transaction": unicode,
        }
        self.fieldnames = None
        self.keys_to_validate = self.conversion_dict.keys()
        self.result_row_list = []
        self.datas = datas
        self.type = None
        if sogen_type == 'paypal':
            self.type = 'PAYPAL'
        elif sogen_type == 'amex':
            self.type = 'AMEX'

    def parse(self):
        self.datas = self.datas.decode('iso-8859-15').encode('utf-8')
        self.datas = self.datas.replace('="', '').replace('"', '')
        csv_file = tempfile.NamedTemporaryFile()
        csv_file.write(self.datas)
        csv_file.flush()
        with open(csv_file.name, 'rU') as fobj:
            reader = UnicodeDictReader(fobj, fieldnames=self.fieldnames)
            self.result_row_list = list(reader)
        parsed_cols = self.result_row_list[0].keys()
        for col in self.keys_to_validate:
            if col not in parsed_cols:
                raise UserError(_('Column %s not present in file') % col)
        res = []
        for line in self.result_row_list:
            for rule in self.conversion_dict:
                if self.conversion_dict[rule] == datetime.datetime:
                    try:
                        date_string = line[rule].split(' ')[0]
                        line[rule] = datetime.datetime.strptime(date_string,
                                                       '%Y-%m-%d')
                    except ValueError as err:
                        raise UserError(
                            _("Date format is not valid."
                              " It should be YYYY-MM-DD for column: %s"
                              " value: %s \n \n \n Please check the line with "
                              "ref: %s \n \n Detail: %s") %
                            (rule, line.get(rule, _('Missing')),
                             line.get('ref', line), repr(err)))
                else:
                    try:
                        line[rule] = self.conversion_dict[rule](line[rule])
                    except Exception as err:
                        raise UserError(
                            _("Value %s of column %s is not valid.\n Please "
                              "check the line with ref %s:\n \n Detail: %s") %
                            (line.get(rule, _('Missing')), rule,
                             line.get('ref', line), repr(err)))
            
            if line["Type de carte"] == self.type \
                    and line["Etat de la transaction"] != u"refusée":
                res.append(line)
        self.result_row_list = res
        self._post()

    def _post(self):
        return
