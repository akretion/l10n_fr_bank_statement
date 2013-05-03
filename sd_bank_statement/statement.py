# -*- coding: utf-8 -*-
###############################################################################
#
#   sd_bank_statement for OpenERP
#   Copyright (C) 2013-TODAY Akretion <http://www.akretion.com>.
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
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

from openerp.osv import fields, orm


class AccountStatementProfil(orm.Model):
    _inherit = "account.statement.profile"

    def statement_import(self, cr, uid, ids, profile_id, file_stream, ftype="csv", context=None):
        if context is None:
            context = {}
        context['account_to_escape'] = ['30789702183']
        return super(AccountStatementProfil, self).statement_import(cr, uid, ids,\
                    profile_id, file_stream, ftype=ftype, context=context)
 
