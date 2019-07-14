import os
import re
import sys
import openpyxl

import numpy as np
import pandas as pd

from datetime import datetime

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

from .. import data

with pkg_resources.path(data, 'clinical_neuroscore_v3d0_variables.tsv') as data_file:
    VARIABLES = pd.read_csv(data_file, sep='\t')
DATE_COL = 5

def parse_neuroscore_v3d0(wb, exam, debug=False):
    """
    Parses neuroscore workbook, primarily the Template worksheet

    **Parameters**

        wb
            an openpyxl workbook, speed is greatly improved when 
            read_only=True and maybe data_only=True
        exam
            The template worksheet has up to 3, possibley more, visit
            (known as exams in th worksheet) data sets. This controls which
            exam is parsed. It is ***zero-based*** indexing.
        debug
            This controls whether to parse the exam date. It allows for testing
            without setting the date.

    **Outputs**
        date
            The date of the exam. This is for file naming purposes. The date
            first date is assumed to be in cell(9, E). The column is two
            columns combined to 1, so we should note the behavior of this.
        results
            A dataframe. The columns are the measured variables. The rows are
            participants. They should be identified by some random string so
            they are deidentified.
    """

    col_adj = exam * 4
    results = pd.DataFrame({x: [np.nan] for x in VARIABLES['redcap']})

    defined_variables = VARIABLES[(~VARIABLES['row'].isnull()) &
                                  (~VARIABLES['column'].isnull())]
    defined_variables['column'] = defined_variables['column'] + col_adj
    worksheets = pd.unique(defined_variables['worksheet'])
    if any(pd.isnull(worksheets)):
        raise Exception('There are unassigned worksheets in {}'.format(data_file))

    for ws in worksheets:
        sheet = wb[ws]
        df = defined_variables[defined_variables['worksheet'] == ws]

        results[defined_variables['redcap']] = [
            sheet.cell(row=int(x), column=int(y)).value 
            for x, y in zip(defined_variables['row'], defined_variables['column'])]

    if debug:
        date = '07071986'
    else:
        date = datetime(wb['Template'].cell(row=9, column=DATE_COL + col_adj).value, 
                        '%d-%b-%Y').strftime('%d%m%Y')

    return date, results
        
def parse_neuroreader_v2d2d8(pdf):
    pass
    
