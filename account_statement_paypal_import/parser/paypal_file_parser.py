# -*- coding: utf-8 -*-
###############################################################################
#
#   account_statement_paypal_import for OpenERP
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


class PAYPALFileParser(FileParser):
    """
    Standard parser that use a define format in csv or xls to import into a
    bank statement. This is mostely an example of how to proceed to create a new
    parser, but will also be useful as it allow to import a basic flat file.
    """

    def __init__(self, parse_name, ftype='csv'):
        conversion_dict = {
            u'Date': {
                'type': datetime.datetime,
                'format': "%d/%m/%Y",
            },
            u' Nom': unicode,
            u' Type': unicode,
            u' Avant commission': float,
            u' Commission': float,
            u' Net': float,
            u" De l'adresse email": unicode,
            u" À l'adresse email": unicode,
            u' N° de transaction': unicode,
            u' Nº de facture': unicode,
            u" État" : unicode,
        }
        #TODO FIXME
        header = [

                u"Date",u" Heure",u" Fuseau horaire",u" Nom",u" Type",u" État",u" Devise",u" Avant commission",u" Commission",u" Net",u" De l'adresse email",u" À l'adresse email",u" N° de transaction",u" Statut de l'autre partie",u" État de l'adresse",u" Titre de l'objet",u" Numéro d'objet",u" Montant de la livraison et du traitement",u" Montant de l'assurance",u" TVA",u" Nom Option 1",u" Valeur Option 1",u" Nom Option 2",u" Option 2 Valeur",u" Site d'enchères",u" Pseudo de l'acheteur",u" URL de l'objet",u" Date de clôture",u" Numéro de tiers de confiance",u" N° de facture",u" Nº de transaction de référence",u" Nº de facture",u" Nº de client",u" Numéro d'avis de réception",u" Solde",u" Adresse 1",u" Adresse 2/district/quartier",u" Ville",u" État/Province/Région/Comté/Territoire/Préfecture/République",u" Code postal",u" Pays",u" Numéro de téléphone à contacter",u" "

                ]
        super(PAYPALFileParser,self).__init__(parse_name, ftype=ftype,
                                              conversion_dict=conversion_dict)

    @classmethod
    def parser_for(cls, parser_name):
        """
        Used by the new_bank_statement_parser class factory. Return true if
        the providen name is generic_csvxls_so
        """
        return parser_name == 'paypal_csvparser'

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
        if line[u' N\xba de facture']:
            ref = "krap_%s"%line[u' N\xba de facture']
        else:
            ref = "/"
        res = {
            'name': line.get(u' N\xb0 de transaction', '/'),
            'date': line.get(' Date', datetime.datetime.now().date()),
            'amount': line.get(' Avant commission', 0.0),
            'ref': ref,
            'partner_name': line.get(' Nom', '/'),
            'paypal_payment_type': line.get(' Type', '/'),
            'email_from': line.get(" De l'adresse email", '/'),
            'email_to': line.get(u" \xc0 l'adresse email", '/'),
            'transaction_number': line.get(u' N\xb0 de transaction', '/'),
  #          'invoice_number': line.get(' Nº de facture', '/'),
            'commission_amount':line.get(' Commission', 0.0),
            'transaction_state': line.get(u' État', '/'),
        }
        return res
