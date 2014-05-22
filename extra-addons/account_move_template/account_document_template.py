# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
from tools.translate import _

class account_document_template(osv.osv):

    _computed_lines = {}
    _current_template_id = 0
    _cr = None
    _uid = None
    _name = 'account.document.template'

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        }

    def _input_lines(self, cr, uid, template):
        count = 0
        for line in template.template_line_ids:
            if line.type == 'input':
                count += 1
        return count

    def _get_template_line(self, cr, uid, template_id, line_number):
        for line in self.browse(cr, uid, template_id).template_line_ids:
            if line.sequence == line_number:
                return line
        return False

    def _generate_empty_lines(self, cr, uid, template_id):
        lines = {}
        for template_line in self.browse(cr, uid, template_id).template_line_ids:
            lines[template_line.sequence] = None
        return lines

    def lines(self, line_number):
        if self._computed_lines[line_number] is not None:
            return self._computed_lines[line_number]
        line = self._get_template_line(self._cr, self._uid, self._current_template_id, line_number)
        self._computed_lines[line_number] = eval(line.python_code.replace('L', 'self.lines'))
        return self._computed_lines[line_number]

    def compute_lines(self, cr, uid, template_id, input_lines):
        # input_lines: dictionary in the form {line_number: line_amount}
        # returns all the lines (included input lines) in the form {line_number: line_amount}
        template = self.browse(cr, uid, template_id)
        if len(input_lines) != self._input_lines(cr, uid, template):
            raise osv.except_osv(_('Error'),
                _('Inconsistency between input lines and filled lines for template %s') % template.name)
        self._current_template_id = template.id
        self._cr = cr
        self._uid = uid
        self._computed_lines = self._generate_empty_lines(cr, uid, template_id)
        self._computed_lines.update(input_lines)
        for line_number in self._computed_lines:
            self.lines(line_number)
        return self._computed_lines

account_document_template()

class account_document_template_line(osv.osv):

    _name = 'account.document.template.line'

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'sequence': fields.integer('Number', required=True),
        'type': fields.selection([('computed', 'Computed'),('input', 'User input')], 'Type', required=True),
        'python_code':fields.text('Python Code'),
        }

account_document_template_line()
