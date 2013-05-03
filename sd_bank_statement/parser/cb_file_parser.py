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

from openerp.addons.account_statement_cb_import.parser.cb_file_parser import CBFileParser

original_post = CBFileParser._post

def _post(self, *args, **kwargs):
    res = original_post(self, *args, **kwargs)
    for line in self.result_row_list:
        if not line.get('type') and not line['ORDER_ID'][0:3] == 'DEV':
            line['ORDER_ID'] = 'DEV-%s'%line['ORDER_ID']
    return res

CBFileParser._post = _post
