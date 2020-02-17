import openpyxl

import pandas as pd

def ped_initialize_lut(excel):
    """
    Initialize a blank lookup table for the pediatric neuroscore file.

    **Parameters**

        excel
            Excel file name point to a ped mcwscore file.

    **Outputs**

        output
            A dataframe with the following columns:
                test - the test name the row belongs
                test_no - the current test number
                identifier - the unique identifier for the row
    """
    output = {'test': [], 'test_no': [], 'identifier': []}
    test_counter = {}
    TEST_COL = 2
    RAW_COL = 3

    wb = openpyxl.load_workbook(excel, data_only=True)
    sh = wb['Template']

    begin_line = 1
    while ((not sh[begin_line] or 
        not sh[begin_line][RAW_COL].value or
        sh[begin_line][RAW_COL].value.strip() != "Raw") and 
        begin_line < sh.max_row):

        begin_line = begin_line + 1

    while ((not sh[begin_line] or 
        not sh[begin_line][TEST_COL].value) and
        begin_line < sh.max_row):

        begin_line = begin_line + 1

    print(f'begin_line : {begin_line}')
            
    if begin_line < sh.max_row:

        current_test = sh[begin_line][TEST_COL].value
        if current_test in test_counter:
            test_counter[current_test] += 1
        else:
            test_counter[current_test] = 1

        unique_stack = [sh[begin_line][TEST_COL].value]
        p_indent = sh[begin_line][TEST_COL].alignment.indent
        indent_mapper = {p_indent: 0}
        p_indent_key = p_indent

        output['identifier'].append(' | '.join(unique_stack))
        output['test'].append(current_test)
        output['test_no'].append(test_counter[current_test])

        for current_line in range(begin_line + 1, sh.max_row + 1):

            if (sh[current_line] and 
                sh[current_line][TEST_COL].value and 
                sh[current_line][TEST_COL].value.strip()):

                c_text = sh[current_line][TEST_COL].value

                c_indent = sh[current_line][TEST_COL].alignment.indent
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

                output['identifier'].append(' | '.join(unique_stack))
                output['test'].append(current_test)
                output['test_no'].append(test_counter[current_test])

                p_indent = c_indent

    return output

class lut:
    def __init__(self, excel):
        self.excel = excel
        self.df_lut = pd.read_excel(self.excel)
        self.dict_lut = self.convert_dflut_to_dictlut()
        self.split_identifiers = [x.split(' | ') 
                                  for x in self.df_lut['identifier']]


    def get_headers_at_indent_level(self, level):
        """Returns all headers at indent level `level`"""

        return ['' if len(x) < (level + 1) else x[level] 
                for x in self.split_identifiers]

class aphasia_lut(lut):
    def __init__(self, excel):
        super.__init__()
        self.dict_lut = self.convert_dflut_to_dictlut()

    def convert_dflut_to_dictlut(self):
        """Converts a df lut to a dict lut"""
        identifier_loc = self.df_lut.columns.isin(['identifier'])
        rc_cols = self.df_lut.columns[~identifier_loc]

        values = self.df_lut.fillna({x:'' for x in rc_cols})[rc_cols].values.tolist()
        results = {x:y for x,y in zip(self.df_lut['identifier'], values)}

        return results
    

class ped_lut(lut):
    def __init__(self, excel):
        super.__init__()
        self.dict_lut = self.convert_dflut_to_dictlut()

    def convert_dflut_to_dictlut(self):
        """Converts a df lut to a dict lut"""
        data_cols = ['raw', 'ss', 'percentile', 'equivalent', 'form', 'notes']

        values = self.df_lut.fillna({x:'' for x in data_cols})[data_cols].values.tolist()
        results = {(identifier, test_no): values 
                   for identifier, test_no, values 
                   in zip(self.df_lut['identifier'], 
                          self.df_lut['test_no'], 
                          values)}

        return results

    

    

    
        
