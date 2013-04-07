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


class DailyPAYPALFileParser(FileParser):
    """
    Standard parser that use a define format in csv or xls to import into a
    bank statement. This is mostely an example of how to proceed to create a new
    parser, but will also be useful as it allow to import a basic flat file.
    """

    def __init__(self, parse_name, ftype='csv'):
        conversion_dict = {
            u"Numéro de transaction": unicode,
            u"Numéro de facture": unicode,
            u"Code de transaction": unicode,
            u"Date de fin de transaction": {
                        'type': datetime.datetime,
                        'format': "%Y/%m/%d %H:%M:%S +%f",
            },
            u"Transaction débitée ou créditée": unicode,
            u"Montant brut de la transaction": float,
            u"Montant de la commission": float,
            u"État de la transaction": unicode,
            u"Numéro de compte du payeur": unicode,
            u"Prénom": unicode,
            u"Nom": unicode,
        }
        #TODO FIXME
        header = [
                "CH","Numéro de transaction","Numéro de facture","Numéro de référence PayPal","Type de numéro de référence PayPal","Code de transaction","Date de début de la transaction","Date de fin de transaction","Transaction débitée ou créditée","Montant brut de la transaction","Devise de la transaction","Commission débitée ou créditée","Montant de la commission","Devise de la commission","État de la transaction","Montant de l'assurance","Montant de la TVA","Montant de la livraison","Objet de la transaction","Remarque sur la transaction","Numéro de compte du payeur","État de l'adresse du payeur","Nom de l'objet","Numéro de l'objet","Nom de l'option 1","Valeur de l'option 1","Nom de l'option 2","Valeur de l'option 2","Site d'enchère","Pseudo de l'acheteur","Date de clôture des enchères","Adresse de livraison - Ligne 1","Adresse de livraison - Ligne 2","Adresse de livraison - Ville","Adresse de livraison - État","Adresse de livraison - Code postal","Adresse de livraison - Pays","Mode de livraison","Champ personnalisé","Adresse de facturation, ligne 1","Adresse de facturation, ligne 2","Ville de facturation","État de facturation","Code postal de facturation","Pays de facturation","Identifiant utilisateur","Prénom","Nom","Dénomination sociale de l'utilisateur","Type de carte","Source de paiement","Nom du destinataire de la livraison","État de vérification de l'autorisation","Eligibilité à la protection","N° du suivi des paiements","Identifiant de la boutique","Identifiant du terminal","Bons d'achat","Offres spéciales","Numéro de la carte de fidélité","Type de paiement","Adresse de livraison secondaire - Ligne 1","Adresse de livraison secondaire - Ligne 2","Adresse de livraison secondaire - Ville","Adresse de livraison secondaire - État","Adresse de livraison secondaire - Pays","Adresse de livraison secondaire - Code postal","Numéro de Référence du prestataire de service tiers",

                ]

        ftype = 'csv'
        super(DailyPAYPALFileParser,self).__init__(parse_name, ftype=ftype,
                                           conversion_dict=conversion_dict)

    @classmethod
    def parser_for(cls, parser_name):
        """
        Used by the new_bank_statement_parser class factory. Return true if
        the providen name is generic_csvxls_so
        """
        return parser_name == 'daily_paypal_csvparser'

    def _pre(self, *args, **kwargs):
        split_file = self.filebuffer.split("\n")
        selected_lines = ""
        for line in split_file:
            if line.startswith('"CH"') or line.startswith('"SB"'):
                if selected_lines:
                   selected_lines += "\n%s"%line
                else:
                    selected_lines = line
        self.filebuffer = selected_lines

    def _post(self, *args, **kwargs):
        """
        Remove pending lines
        """
        good_row_list = []
        for row in self.result_row_list:
            if not row[u'État de la transaction'] == "P":
                good_row_list.append(row)
        self.result_row_list = good_row_list
        return super(DailyPAYPALFileParser, self)._post(*args, **kwargs)


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
        if line[u"Numéro de facture"]:
            ref = "krap_%s"%line[u"Numéro de facture"]
        else:
            ref = "/"

        partner_name = ""
        if line[u"Prénom"]:
            partner_name = "%s "%line[u"Prénom"]
        if line[u"Nom"]:
            partner_name = partner_name + "%s"%line[u"Nom"]

        amount = line.get(u"Montant brut de la transaction", 0.0)/100
        if line[u"Transaction débitée ou créditée"] == 'DR':
            amount = -amount

        res = {
            'name': line.get(u"Numéro de transaction", '/'),
            'date': line.get(u"Date de fin de transaction", datetime.datetime.now().date()),
            'amount': amount,
            'ref': ref,
            'partner_name': partner_name or "/",
            'paypal_payment_type': line.get(u"Code de transaction", '/'),
            'email_from': line.get(u"Numéro de compte du payeur", '/'),
            'transaction_number': line.get(u"Numéro de transaction", '/'),
            'commission_amount': line.get(u"Montant de la commission", 0.0)/100,
            'transaction_state': line.get(u"État de la transaction", '/'),
        }
        return res
