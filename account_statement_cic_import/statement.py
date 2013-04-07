# -*- coding: utf-8 -*-
###############################################################################
#
#   account_statement_cic_import for OpenERP
#   Copyright (C) 2012 Akretion Benoît GUILLOT <benoit.guillot@akretion.com>
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

from openerp.osv import orm, fields


class AccountStatementProfil(orm.Model):
    _inherit = "account.statement.profile"

    def get_import_type_selection(self, cr, uid, context=None):
        """
        Has to be inherited to add parser
        """
        res = super(AccountStatementProfil, self).get_import_type_selection(cr, uid, context=context)
        res.extend([('cic_csvparser', 'Parser for CIC import statement'),
            ])
        return res


class account_bank_statement_line(orm.Model):
    _inherit = "account.bank.statement.line"

    _columns = {
    }


class AccountBankStatement(orm.Model):
    _inherit = "account.bank.statement"


class AccountStatementCompletionRule(orm.Model):
    _inherit = "account.statement.completion.rule"

    def get_functions(self, cr, uid, context=None):
        res = super(AccountStatementCompletionRule, self).get_functions(cr, uid, context=context)
        res.extend([])
        return res
