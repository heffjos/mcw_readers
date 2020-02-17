import openpyxl

import pandas as pd

NAN_VALUES = ['#N/A', '#REF!', '#VALUE!', None, 'RAW', 'Score', '']
    

class wb_parser:
    def __init__(self, wb_fname):
        self.fname = wb_fname
        self.wb = openpyxl.load_workbook(self.fname, data_only=True)
        self.sh = self.wb['Template']
        self.unhidden_rows = [row for row, rd in self.sh.row_dimensions.items() 
                              if not rd.hidden]

class aphasia_wb_parser(wb_parser):
    def __init__(self, wb_fname):
        super().__init__(wb_fname)

        self.first_data_line = self.get_first_data_line()
        if self.first_data_line > self.sh.max_row:
            pass

        self.unhidden_rows_with_data = [x for x in self.unhidden
                                        if x >= self.first_data_line and
                                        self.sh[x] and 
                                        self.sh[x][1].value and
                                        self.sh[x][1].value.strip()]

        self.unhidden_identifiers = self.get_unhidden_identifiers()

    def get_first_data_line(self):
        """Returns the first line of data entry"""

        col_stop1 = 2
        col_stop2 = 1

        for i in range(1, self.sh.max_row + 1):
            if self.sh[i] and self.sh[i][col_stop1].value == "Raw":
                break

        for i in range(i + 1, self.sh.max_row + 1):
            if self.sh[i] and self.sh[i][col_stop2].value:
                break

        return i

    def get_identifiers(self, rows):
        """Returns unique data entry line identifiers for rows in wb"""
        col = 1

        output = []

        for i, current_line in enumerate(rows):
            if not (self.sh[current_line] and
                self.sh[current_line][col].value and
                self.sh[current_line][col].value.strip() and
                not self.sh[current_line][col].value.strip().startswith('*')):

                pass

            else:
                break


        unique_stack = [self.sh[rows[i]][col].value]
        p_indent = self.sh[rows[i]][col].alignment.indent
        output.append((" | ".join(unique_stack), rows[i]))

        for current_line in rows[(i + 1):]:

            if (self.sh[current_line] and
                self.sh[current_line][col].value and
                self.sh[current_line][col].value.strip() and
                not self.sh[current_line][col].value.strip().startswith('*')):

                c_text = self.sh[current_line][col].value

                print(f"Parsing line : {current_line} : {c_text}")

                c_indent = self.sh[current_line][col].alignment.indent
                if c_text.startswith(' '):
                    c_indent = c_indent + 1
                c_text = c_text.strip()

                if c_indent == p_indent:
                    unique_stack.pop()
                    unique_stack.append(c_text)
                elif c_indent > p_indent:
                    unique_stack.append(c_text)
                else:
                    if c_indent == 0:
                        unique_stack.clear()
                    else:
                        unique_stack.pop()
                        unique_stack.pop()

                    unique_stack.append(c_text)

                output.append((" | ".join(unique_stack), current_line))
                p_indent = c_indent

        return output

    def get_all_identifiers(self):
        """Returns all unique data entry line identifiers in wb"""

        return self.get_identifiers(range(self.first_data_line + 1,
                                          self.sh.max_row + 1))

    def get_unhidden_identifiers(self):
        """Returns unhidden unique data entry line identifers in wb"""

        return self.get_identifiers(self.unhidden_rows_with_data)

    def get_new_identifiers(self, aphasia_lut):
        """Return new identifiers in sh not found in aphasia_lut"""

        identifiers = self.get_all_identifiers()
        
        new_identifiers = [identfier for identifier, line in identifiers
                           if identifier not in aphasia_lut.dict_lut]

        return new_identifiers

    def get_administered_tests(self):
        """Returns the administered test found in sh"""

        return [x for x, y in self.unhidden_identifiers
                if len(x.split(' | ')) == 1]

    def parse_data(self, aphasia_lut, tp):
        """Parse the data in sh using aphasia_lut for timepoint tp"""

        tp_offset = 4 * (tp - 1)
        col_offset = 2 + tp_offset

        results = {}

        for identifier, row_num in self.unhidden_identifiers:
            rc_variables = aphasia_lut.dict_lut[identifier]

            for n, variable in enumerate(rc_variables):
                if variable:
                    results[variable] = self.sh[row_num][n + col_offset].value

        return results

class peds_wb_parser(wb_parser):
    def __init__(self, wb_fname):
        super().__init__(wb_fname)

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
                           if identifier not in ped_lut.dict_lut]

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

            if identifier in ped_lut.dict_lut:
                rc_variables = ped_lut.dict_lut[identifier]

                for n, variable in enumerate(rc_variables):
                    if variable:
                        results[variable] = self.sh[row_num][raw_col + n].value
                        if results[variable] in NAN_VALUES:
                            results[variable] = pd.np.nan
            else:
                new_identifiers['identifier'].append(identifier[0])
                new_identifiers['test_no'].append(identifier[1])

        return results, new_identifiers

