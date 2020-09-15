from datetime import datetime
from collections import namedtuple

import openpyxl

import pandas as pd

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

from .lut import lut
from .. import data

NAN_VALUES = ['#N/A', '#REF!', '#VALUE!', None, 'RAW', 'Score', '']

line = namedtuple('line', 'identifier test_no row')

class wb_parser():

    NAN_VALUES = {
        ' --',
        '%tile',
        '9-Min',
        'BLUE',
        'Can.',
        'FM-1',
        'L',
        'LIM.',
        None,
        'Norm',
        'Performance Indicator',
        'R',
        'SS',
        'STD',
        '[ERR]',
        '[FORM]',
        '[NORM]',
        '[SPAN]',
        '[TIME]',
        'raw',
        'val',
    }

    COL_NAMES = ['raw', 'ss', 'percentile', 'notes']

    def __init__(self, wb_fname):

        self.fname = wb_fname
        self.wb = openpyxl.load_workbook(self.fname, data_only=True)
        self.sh = self.wb['Template']

        self.first_data_row = self.find_first_data_row()
        if self.first_data_row > self.sh.max_row:
            raise Exception('first_data_row > sh.max_row')

        rd = self.sh.row_dimensions
        self.lines = self.parse_lines()
        self.unhidden_lines = [x for x in self.lines
                               if not rd[x.row].hidden]

    def find_first_data_row(self):
        """Returns the first line number of data entry"""

        col_stop1 = 2
        col_stop2 = 1

        for i in range(1, self.sh.max_row + 1):
            if self.sh[i] and self.sh[i][col_stop1].value == "Raw":
                break

        for i in range(i + 1, self.sh.max_row + 1):
            if self.sh[i] and self.sh[i][col_stop2].value:
                break

        return i

    def parse_lines(self):
        """Returns unique data entry line identifiers in wb"""
        col = 1

        output = []
        test_counter = {}

        # process first line here
        current_test = self.sh[self.first_data_row][col].value
        test_counter[current_test] = 1

        unique_stack = [self.sh[self.first_data_row][col].value]
        p_indent = self.sh[self.first_data_row][col].alignment.indent
        indent_mapper = {p_indent: 0}
        p_indent_key = p_indent

        output.append(line(" | ".join(unique_stack), 
                           test_counter[current_test],
                           self.first_data_row))

        for current_line in range(self.first_data_row + 1, 
                                  self.sh.max_row + 1):

            if (self.sh[current_line] and
                self.sh[current_line][col].value and
                self.sh[current_line][col].value.strip() and
                not self.sh[current_line][col].value.strip().startswith('*')):

                c_text = self.sh[current_line][col].value

                c_indent = self.sh[current_line][col].alignment.indent
                if c_text.startswith(' '):
                    c_indent = c_indent + 1

                if c_indent not in indent_mapper:
                    indent_mapper[c_indent] = indent_mapper[p_indent_key] + 1
                    p_indent_key = c_indent
                c_indent = indent_mapper[c_indent]

                print(f"Parsing line : {current_line} : {c_text} : {c_indent}")

                c_text = c_text.strip()

                if c_indent == p_indent:
                    unique_stack.pop()
                    unique_stack.append(c_text)

                    if c_indent == 0:
                        current_test = c_text
                        if current_test in test_counter:
                            test_counter[current_test] += 1
                        else:
                            test_counter[current_test] = 1
                        
                elif c_indent > p_indent:
                    unique_stack.append(c_text)
                else:
                    if c_indent == 0:
                        unique_stack.clear()

                        current_test = c_text
                        if current_test in test_counter:
                            test_counter[current_test] += 1
                        else:
                            test_counter[current_test] = 1

                        indent_mapper = {c_indent: 0}
                        p_indent_key = c_indent
                    else:
                        unique_stack.pop()
                        unique_stack.pop()

                    unique_stack.append(c_text)

                output.append(line(' | '.join(unique_stack), 
                                   test_counter[current_test],
                                   current_line))

                p_indent = c_indent

        return output

    def find_new_lines(self, lut):
        """Return new lines in sh not found in lut"""

        new_lines = [line for identifier, test_no, row in self.lines
                     if identifier not in lut.lut]

        return new_lines

    def find_administered_tests(self):
        """Returns the administered test found in sh"""

        return [identifier for identifier, _, _ in self.unhidden_lines
                if identifier.find(' | ') == -1]

    def parse_data(self, lut, tp):
        """Parse the data in sh using lut for timepoint tp"""

        results = {}
        tp_offset = 4 * (tp - 1)
        col_offset = 2 + tp_offset
        new_lines = {'identifier': [],
                     'test_no': [],
                     'row': [],}
        missing_lines = {'identifier': [],
                         'test_no': [],
                         'row': [],
                         'col': [],
                         'name': [],
                         'value': [],}

        for identifier, test_no, row in self.unhidden_lines:
            key = (identifier, test_no)
            if key in lut.lut:
                rc_variables = lut.lut[key]

                for n, variable in enumerate(rc_variables):
                    try:
                        value = self.sh[row][n + col_offset].value
                        if value in self.NAN_VALUES:
                            value = pd.np.nan
                    except:
                        value = pd.np.nan

                    if variable:
                        results[variable] = [value]
                    elif not pd.isna(value):
                        missing_lines['identifier'].append(identifier)
                        missing_lines['test_no'].append(test_no)
                        missing_lines['row'].append(row)
                        missing_lines['col'].append(n + col_offset)
                        missing_lines['name'].append(self.COL_NAMES[n])
                        missing_lines['value'].append(value)
                        
            else:
                new_lines['identifier'].append(identifier)
                new_lines['test_no'].append(test_no)
                new_lines['row'].append(row)
                    
        return results, new_lines, missing_lines

    def parse_header(self, tp, study):
        """Parse header information for timepoint tp and study study"""

        results = {}

        if study == 'epilepsy':
            date_col = 4 + (tp - 1) * 4
            age_col = 2 + (tp -1) * 4

            results['testdat'] = self.sh[9][date_col].value.strftime('%Y-%m-%d')
            results['age'] = [int(self.sh[11][age_col].value
                                  .split(',')[0]
                                  .split(': ')[1])]
        else:
            raise Exception(f'Unkown study: {study}')

        return results
    

class peds_wb_parser():

    def __init__(self, wb_fname):
        self.fname = wb_fname
        self.wb = openpyxl.load_workbook(self.fname, data_only=True)
        self.sh = self.wb['Template']

        self.first_data_line = self.get_first_data_line()
        if self.first_data_line > self.sh.max_row:
            pass

        self.identifiers = self.get_all_identifiers()

    def get_first_data_line(self):
        """Returns the first line of data entry"""

        col_stop1 = 3
        col_stop2 = 2

        for i in range(1, self.sh.max_row + 1):
            if self.sh[i] and self.sh[i][col_stop1].value == "Raw":
                break

        for i in range(i + 1, self.sh.max_row + 1):
            if self.sh[i] and self.sh[i][col_stop2].value:
                break

        return i

    def get_all_identifiers(self):
        """Returns unique data entry line identifiers in wb"""
        col = 2

        output = []
        test_counter = {}

        # process first line here
        current_test = self.sh[self.first_data_line][col].value
        if current_test in test_counter:
            test_counter[current_test] += 1
        else:
            test_counter[current_test] = 1

        unique_stack = [self.sh[self.first_data_line][col].value]
        p_indent = self.sh[self.first_data_line][col].alignment.indent
        indent_mapper = {p_indent: 0}
        p_indent_key = p_indent

        output.append(((" | ".join(unique_stack), test_counter[current_test]),
                      self.first_data_line))

        for current_line in range(self.first_data_line + 1, self.sh.max_row):

            if (self.sh[current_line] and
                self.sh[current_line][col].value and
                self.sh[current_line][col].value.strip()):

                c_text = self.sh[current_line][col].value

                c_indent = self.sh[current_line][col].alignment.indent
                if c_text.startswith(' '):
                    c_indent = c_indent + 1

                if c_indent not in indent_mapper:
                    indent_mapper[c_indent] = indent_mapper[p_indent_key] + 1
                    p_indent_key = c_indent
                c_indent = indent_mapper[c_indent]

                print(f"Parsing line : {current_line} : {c_text} : {c_indent}")

                c_text = c_text.strip()

                if c_indent == p_indent:
                    unique_stack.pop()
                    unique_stack.append(c_text)

                    if c_indent == 0:
                        current_test = c_text
                        if current_test in test_counter:
                            test_counter[current_test] += 1
                        else:
                            test_counter[current_test] = 1
                        
                elif c_indent > p_indent:
                    unique_stack.append(c_text)
                else:
                    if c_indent == 0:
                        unique_stack.clear()

                        current_test = c_text
                        if current_test in test_counter:
                            test_counter[current_test] += 1
                        else:
                            test_counter[current_test] = 1

                        indent_mapper = {c_indent: 0}
                        p_indent_key = c_indent
                    else:
                        unique_stack.pop()
                        unique_stack.pop()

                    unique_stack.append(c_text)

                output.append(((' | '.join(unique_stack), test_counter[current_test]),
                              current_line))

                p_indent = c_indent

        return output

    def get_new_identifiers(self, ped_lut):
        """Return new identifiers in sh not found in ped_lut"""

        new_identifiers = [identfier for identifier, line in self.identifiers
                           if identifier not in ped_lut.lut]

        return new_identifiers

    def get_administered_tests(self):
        """Returns the administered test found in sh"""

        return [x[0] for x, y in self.identifiers
                if len(x[0].split(' | ')) == 1]

    def parse_data(self, ped_lut):
        """Parse the data in sh using ped_lut"""

        raw_col = 3
        results = {}
        new_identifiers = {'identifier': [],
                           'test_no': []}

        for identifier, row_num in self.identifiers:

            if identifier in ped_lut.lut:
                rc_variables = ped_lut.lut[identifier]

                for n, variable in enumerate(rc_variables):
                    if variable:
                        results[variable] = self.sh[row_num][raw_col + n].value
                        if results[variable] in NAN_VALUES:
                            results[variable] = pd.np.nan
            else:
                new_identifiers['identifier'].append(identifier[0])
                new_identifiers['test_no'].append(identifier[1])

        return results, new_identifiers

    def parse_default_data(self):
        """Parses the data in sh with the package ped_lut"""

        with pkg_resources.path(data, 'ped_lut.xlsx') as data_file:
            current_lut = ped_lut(data_file)

        results, new_identifiers = self.parse_data(current_lut)

        return results, new_identifiers
        

