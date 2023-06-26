import re

from datetime import datetime
from collections import namedtuple

import openpyxl

import numpy as np
import pandas as pd

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

from mcw_readers.interfaces.lut import lut
from mcw_readers import data
from mcw_readers.utils import DF_PSYCHOMETRIC, DICT_PSYCHOMETRIC, close_any

line = namedtuple('line', 'identifier test_no row')

class PedsParserError(Exception):
    """Exception raised if there is an error while parsing a peds neuroscore file"""
    pass

def peds_determine_variable_value(value, rc_variables, percentile):
    """
    Determines the variable value for 'ss' column
    
    Parameters
    ----------
    
    value : float
        the cell value
    rc_variables : list of str
        the list of redcap variables for the row of cell
    percentile : float
        the percentile value for the current row.
    
    Returns
    -------
    
    rc_variable : str
        the redcap variable name
    postprocessed_value : str or float
        the postprocessed cell value
    
    Description
    -----------
    
    Here are the lut columns associated with ss:
        standard_score: [49, 150]
        scaled_score:   [1,20]
        t_score:        [19, 80]
    """

    if ~np.isnan(percentile):
        standard_scores = DICT_PSYCHOMETRIC['standard_score'][percentile]
        scaled_scores = DICT_PSYCHOMETRIC['scaled_score'][percentile]
        t_scores = DICT_PSYCHOMETRIC['t_score'][percentile]
        
        if (value in standard_scores or
            (percentile == 1 and (value < 67 and value >= 32))):
        
            variable_values = [
                (rc_variables[1], value),
                (rc_variables[2], None),
                (rc_variables[3], None),
            ]
        elif (value in scaled_scores or 
              close_any(value, scaled_scores, 3) or
              (percentile == 1 and (value < 4 and value > 0))):
        
            variable_values = [
                (rc_variables[1], None),
                (rc_variables[2], value),
                (rc_variables[3], None),
            ]
        elif (value in t_scores or 
              close_any(value, t_scores, 3) or
              (percentile == 1 and (value < 28 and value > 0))):
        
            variable_values = [
                (rc_variables[1], None),
                (rc_variables[2], None),
                (rc_variables[3], value),
            ]
        else:
            raise PedsParserError()
    elif np.isnan(percentile):
        if value >= 80:
            variable_values = [
                (rc_variables[1], value),
                (rc_variables[2], None),
                (rc_variables[3], None),
            ]
        elif value >= 0 and value < 21:
            variable_values = [
                (rc_variables[1], None),
                (rc_variables[2], value),
                (rc_variables[3], None),
            ]
        elif value > 21 and value < 50:
            variable_values = [
                (rc_variables[1], None),
                (rc_variables[2], None),
                (rc_variables[3], value),
            ]
        else:
            raise PedsParserError()

    return variable_values
    

def peds_get_ss_variable(cell, rc_variables, percentile):
    """
    Returns the redcap variable and postprocessed value for 'ss' column
    
    Parameters
    ----------
    
    cell : Cell
        the cell from an openpyxl sheet
    rc_variables : list of str
        the list of redcap variables for the row of cell
    percentile : float
        the percentile value for the current row.
    
    Returns
    -------
    
    rc_variable : str
        the redcap variable name
    postprocessed_value : str or float
        the postprocessed cell value
    
    Description
    -----------
    
    Here are the lut columns associated with ss:
        standard_score
            between [49, 150]
        scaled_score
            between [1,20]
        t_score
            between [19, 80]
            the cell value may start with "T" or "T "
    """
    value = cell.value
    
    if value is not None and value not in neuroscore_parser.NAN_VALUES: 
        print(cell.row, cell.column_letter, value, cell.data_type)

        if cell.data_type == 'n':
            if cell.number_format == '"T"\\ 0;"T"\\ \\-0;"T"\\ 0;"T"\\ @':
                variable_values = [
                    (rc_variables[1], None),
                    (rc_variables[2], None),
                    (rc_variables[3], value),
                ]
            else:    
                variable_values = peds_determine_variable_value(value, rc_variables, percentile)
    
        elif cell.data_type == 's':
            if cell.number_format == '"T"\\ 0;"T"\\ \\-0;"T"\\ 0;"T"\\ @':
                postprocessed_value = float(re.sub('[<>]?[ ]*', '', value.strip()))

                variable_values = [
                    (rc_variables[1], None),
                    (rc_variables[2], None),
                    (rc_variables[3], postprocessed_value),
                ]
            elif re.fullmatch('T[ ]*[>]?\d+', value):
                postprocessed_value = float(re.sub('T[ ]*[>]?', '', value))
    
                variable_values = [
                    (rc_variables[1], None),
                    (rc_variables[2], None),
                    (rc_variables[3], postprocessed_value),
                ]

            elif re.fullmatch('[<>][ ]?\d+', value):
                value = float(re.sub('[<>][ ]?', '', value))
                variable_values = peds_determine_variable_value(value, rc_variables, percentile)

            else:
                variable_values = [(None, value)]
    
        else:
            variable_values = [
                (rc_variables[1], None),
                (rc_variables[2], None),
                (rc_variables[3], None),
            ]
    
    else:
        variable_values = [(None, value)]
    
    return variable_values

class neuroscore_parser():

    NAN_VALUES = {
        '#N/A',
        '#REF!',
        '#VALUE!',
        'RAW',
        'Raw',
        'Equivalent',
        'Form',
        'Notes',
        'Score',
        '',
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
        '<Form>',
        '<Item Set>',
        '<Hand>',
        'Choose One',
    }

    def __init__(self, wb_fname, sheet_name='Template', verbose=True):
        """
        Initializes neuroscore_parser.

        Parameters
        ----------

        wb_fname: str
            path to excel workbook
        verbose : str
            be verboose about doing things

        Attributes
        ----------
            fname : str
                path to exel workbook
            wb : Workbook
                Workbook object for fname
            sh : Sheet
                Sheet object for "Template" in wb
            first_data_row : int
                first line in sh containing data (1-based)
            lines : list of line
                unique data entry lines in sh
            unhidden_lines : list of line
                line objects in lines that are unhidden in sh
        """

        self.fname = wb_fname
        self.wb = openpyxl.load_workbook(self.fname, data_only=True)
        self.sh = self.wb[sheet_name]

        self.first_data_row, self.first_data_col = self.find_first_data()
        if self.first_data_row > self.sh.max_row:
            raise Exception('first_data_row > sh.max_row')

        rd = self.sh.row_dimensions
        self.lines = self.parse_lines(verbose)
        self.unhidden_lines = [x for x in self.lines
                               if not rd[x.row].hidden]

    def find_first_data(self):
        """Returns the row, column for the first data entry"""

        for row, row_cells in enumerate(self.sh.iter_rows(), start=1):
            for col, cell in enumerate(row_cells):
                if cell.data_type == 's' and cell.value == 'Raw':
                    first_row = row + 1
                    first_col = col - 1
                    break
            else:
                continue
            break

        while self.sh[first_row][first_col].data_type == 'n':
            first_row = first_row + 1

        return (first_row, first_col)

    def parse_lines(self, verbose=True):
        """Returns unique data entry line identifiers in wb"""
        col = self.first_data_col

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

                if verbose:
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
        """
        Parse the data in sh using lut for timepoint tp

        Parameters
        ----------

        lut : lut
            The lookup table for parsing.
        tp : int
            The timepoint number
            Used only for epilepsy, dementia, or aphasia depts

        Returns
        -------

        results : dict (variable : [value])
            parsed neuroscore values according to lut
        new_lines : dict
            Each entry contains a new identifier/test_no information
            identifier -> list
            test_no    -> list
            row        -> list
        missing_lines : dict
            Contains neuroscore variables where no redcap variable is assigned,
            but an identifier is present in the lut
            identifier -> list
            test_no    -> list
            row        -> list
            col        -> list
            name       -> list of neuroscore column names
            value      -> neuroscore value
        """

        data_cols = ['raw', 'ss', 'percentile', 'notes']
        tp_offset = 4 * (tp - 1)
        col_offset = 2 + tp_offset
            
        results = {}
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
                            value = np.nan
                    except:
                        value = np.nan

                    if variable:
                        results[variable] = [value]
                    elif not pd.isna(value):
                        missing_lines['identifier'].append(identifier)
                        missing_lines['test_no'].append(test_no)
                        missing_lines['row'].append(row)
                        missing_lines['col'].append(n + col_offset)
                        missing_lines['name'].append(data_cols[n])
                        missing_lines['value'].append(value)
                        
            else:
                new_lines['identifier'].append(identifier)
                new_lines['test_no'].append(test_no)
                new_lines['row'].append(row)
                    
        return results, new_lines, missing_lines

    def parse_header(self, tp, study):
        """Parse header information for timepoint tp and study study"""

        results = {}

        if self.dept in {'peds'}:
            results['Provider'] = self.sh['C4'].value
            results['Psychometrist'] = self.sh['C5'].value

            results['Sex'] = self.sh['G4'].value
            results['DOE'] = self.sh['G5'].value
            results['DOB'] = self.sh['G6'].value
            results['Yrs'] = self.sh['G7'].value
            results['Mo']  = self.sh['G8'].value
            results['D']   = self.sh['G9'].value
            results['Handedness'] =  self.sh['G10'].value

        elif self.dept in {'epilepsy', 'dementia', 'aphasia'}:
            date_col = 4 + (tp - 1) * 4
            age_col = 2 + (tp -1) * 4

            results['testdat'] = self.sh[9][date_col].value.strftime('%Y-%m-%d')
            results['age'] = [int(self.sh[11][age_col].value
                                  .split(',')[0]
                                  .split(': ')[1])]
        else:
            raise Exception(f'Unkown dept: {dept}')

        return results

class mci_parser(neuroscore_parser):

    def parse_date(self, tp):
        """Retrieve the date for a timepoint"""

        for row in range(1, self.sh.max_row + 1):
            for col, cell in enumerate(self.sh[row]):
                if (cell.data_type == 's' and 
                    (cell.value.startswith('DOS A:') or 
                     cell.value.startswith('EXAM A:'))):

                    first_row = row
                    first_col = col
                    break
            else:
                continue
            break

        if cell.value.startswith('DOS A:'):
            row = first_row + tp - 1
            txt = self.sh[row][first_col].value.split(':')[1].strip()

            exam_date = datetime.strptime(txt, '%B %d, %Y').strftime('%Y-%m-%d')
        elif cell.value.startswith('EXAM A:'):
            col = (first_col + 2) + ((tp - 1) * 4)
            exam_date = self.sh[first_row][col].value.strftime('%Y-%m-%d')
        else:
            exam_date = None

        return exam_date
            
class peds_parser(neuroscore_parser):

    def parse_data(self, lut):
        """
        Parse the data in sh using lut

        Parameters
        ----------

        lut : lut
            The lookup table for parsing.

        Returns
        -------

        results : dict (variable : [value])
            parsed neuroscore values according to lut
        new_lines : dict
            Each entry contains a new identifier/test_no information
            identifier -> list
            test_no    -> list
            row        -> list
        missing_lines : dict
            Contains neuroscore variables where no redcap variable is assigned,
            but an identifier is present in the lut
            identifier -> list
            test_no    -> list
            row        -> list
            col        -> list
            name       -> list of neuroscore column names
            value      -> neuroscore value
        """

        data_cols = ['raw', 'ss', '%tile', 'equivalent', 'form', 'notes']
        get_variables = [
            (0, self._get_raw_variable),
            (1, self._get_ss_variable),
            (2, self._get_percentile_variable),
            (3, self._get_equivalent_variable),
            (4, self._get_form_variable),
            (5, self._get_notes_variable),
        ]
            
        results = {}
        debug_results = {
            'identifier': [],
            'variable': [],
            'value': [],
        }
        new_lines = {'identifier': [],
                     'test_no': [],
                     'row': [],}
        missing_lines = {'identifier': [],
                         'test_no': [],
                         'row': [],
                         'col': [],
                         'col_letter': [],
                         'name': [],
                         'value': [],}

        for identifier, test_no, row in self.unhidden_lines:
            key = (identifier, test_no)
            if key in lut.lut:
                rc_variables = lut.lut[key]

                for n, get_variable in get_variables:

                    cell = self.sh[row][n + self.first_data_col + 1]
                    variable_values = get_variable(cell, rc_variables)

                    for variable, value in variable_values:
                        is_nan_value = value in self.NAN_VALUES

                        if variable and not is_nan_value:
                            results[variable] = [value]

                            debug_results['identifier'].append(identifier)
                            debug_results['variable'].append(variable)
                            debug_results['value'].append(value)
                        elif not pd.isna(value) and not is_nan_value:
                            missing_lines['identifier'].append(identifier)
                            missing_lines['test_no'].append(test_no)
                            missing_lines['row'].append(row)
                            missing_lines['col'].append(cell.column)
                            missing_lines['col_letter'].append(cell.column_letter)
                            missing_lines['name'].append(data_cols[n])
                            missing_lines['value'].append(value)

            else:
                new_lines['identifier'].append(identifier)
                new_lines['test_no'].append(test_no)
                new_lines['row'].append(row)

        return results, debug_results, new_lines, missing_lines

    def _get_raw_variable(self, cell, rc_variables):
        """Returns the redcap variable and postprocessed value for raw column"""

        return [(rc_variables[0], cell.value)]

    def _get_ss_variable(self, cell, rc_variables):
        """
        Returns the redcap variable and postprocessed value for 'ss' column

        Parameters
        ----------

        cell : Cell
            the cell from an openpyxl sheet
        rc_variables : list of str
            the list of redcap variables for the row of cell


        Returns
        -------

        rc_variable : str
            the redcap variable name
        postprocessed_value : str or float
            the postprocessed cell value

        Description
        -----------

        Here are the lut columns associated with ss:
            standard_score
                between (60, 120]
            scaled_score
                between [1,35]
            t_score
                between [40, 60]
                the cell value may start with "T" or "T "
        """

        return [(rc_variables[1], cell.value)]

    def _get_percentile_variable(self, cell, rc_variables):
        """Returns the redcap variable and postprocessed value for 'percentile' colum"""

        return [(rc_variables[2], cell.value)]

    def _get_equivalent_variable(self, cell, rc_variables):
        """
        Returns the redcap variables and postprocessed values for 'equivalent' column.

        Parameters
        ----------

        cell : Cell
            the cell from an openpyxl sheet
        rc_variables : list of str
            the list of redcap variables for the row of cell


        Returns
        -------

        rc_variable : str
            the redcap variable name
        postprocessed_value : str or float
            the postprocessed cell value

        Description
        -----------
        The eqiuvalent column is the only column that can return multiple values.
        Here are the columns associated with 'equivalent':
            sign
                <, > will be listed or two values with a dash will be listed
            age_equivalent
                either enter the singal valeu listed or the first value ifa  range
            high_equivalent
                either leave blank if a single value listed or enter the send value of range
        """

        value = cell.value

        if value is not None:
            if cell.data_type == 's':
                if re.match('[<>]', value):
                    variable_values = [
                        (rc_variables[3], value),
                        (rc_variables[4], None),
                        (rc_variables[5], None)
                    ]
                elif re.fullmatch('\d+-\d+', value):
                    variable_values = [
                        (rc_variables[3], value),
                        (rc_variables[4], None),
                        (rc_variables[5], None),
                    ]
                elif re.fullmatch('\d+:\d+', value):
                    m = re.fullmatch('(\d+):(\d+)', value)
                    n1 = float(m.group(1))
                    n2 = float(m.group(2))
                    variable_values = [
                            (rc_variables[3], None),
                            (rc_variables[4], n1 * 12 + n2),
                            (rc_variables[5], None),
                    ]
                elif re.fullmatch('\d+:\d+-\d+:\d+', value):
                    m = re.fullmatch('(\d+):(\d+)-(\d+):(\d+)', value)
                    n1 = float(m.group(1))
                    n2 = float(m.group(2))
                    n3 = float(m.group(3))
                    n4 = float(m.group(4))
                    variable_values = [
                            (rc_variables[3], None),
                            (rc_variables[4], n1 * 12 + n2),
                            (rc_variables[5], n3 * 12 + n4),
                    ]
                else:
                    variable_values = [(None, value)]

            elif cell.data_type == 'n':
                variable_values = [
                    (rc_variables[3], None),
                    (rc_variables[4], float(value)),
                    (rc_variables[5], None),
                ]

            else:
                variable_values = [(None, value)]

        else:
            variable_values = [
                (rc_variables[3], None),
                (rc_variables[4], None),
                (rc_variables[5], None),
            ]

        return variable_values

    def _get_form_variable(self, cell, rc_variables):
        """Returns the redcap variable and postprocessed value for 'form' column"""

        return [(rc_variables[7], cell.value)]

    def _get_notes_variable(self, cell, rc_variables):
        """Returns the redcap variable and postprocesse value for the 'notes' column"""

        return [(rc_variables[8], cell.value)]

