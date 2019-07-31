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
from ..utils import pdftotext
from ..utils import clinical_detect_neuroscore_version
from ..utils import CLINICAL_NEUROREADER_MAPPER

with pkg_resources.path(data, 'clinical_redcap_labeled.tsv') as data_file:
    CLINICAL_VARIABLES = pd.read_csv(data_file, sep='\t')

DATE_COL = 5

def parse_neuroscore(wb, exam, debug=False):
    """
    Parses neuroscore workbook, primarily the Template worksheet

    **Parameters**

        wb
            an openpyxl workbook, speed is greatly improved when 
            read_only=True and maybe data_only=True
        exam
            The template worksheet has up to 3 visits (known as exames in the)
            worksheet) data sets. This controls which exam is parsed. 
            It is ***zero-based*** indexing.
        debug
            This controls whether to parse the exam date. It allows for testing
            without setting the date.

    **Outputs**
        date
            The date of the exam. This is for file naming purposes. The date
            is assumed to be in cell(9, E). The column is two columns combined 
            to 1, so we should note the behavior of this.
        results
            A dataframe. The columns are the measured variables. The rows are
            participants. They should be identified by some random string so
            they are deidentified.
    """
    col_adj = exam * 4
    version = clinical_detect_neuroscore_version(wb)
    if version == None:
        raise Exception('Could not detect clinical neuroscore version')
    df_key = CLINICAL_VARIABLES[CLINICAL_VARIABLES['version'] == version].copy()
    results = pd.DataFrame({x: [np.nan] 
                            for x in pd.unique(CLINICAL_VARIABLES['redcap'])})

    df_key['column'] = df_key['column'] + col_adj
    worksheets = pd.unique(df_key['worksheet'])
    if any(pd.isnull(worksheets)):
        raise Exception('There are unassigned worksheets in {}'.format(data_file))

    for ws in worksheets:
        sheet = wb[ws]
        df = df_key[df_key['worksheet'] == ws]

        results[df_key['redcap']] = [
            sheet.cell(row=int(x), column=int(y)).value 
            for x, y in zip(df_key['row'], df_key['column'])]


    results = results.melt(var_name='variables', value_name='values')
    garbage = results['values'].str.match(r'^=|^raw$|^val$|^\[ERR\]$|^SS$', na=False)
    results['values'][garbage] = np.nan
    results['index'] = 0
    results = results.pivot(index='index', columns='variables', values='values')

    if debug:
        date = '07071977'
    else:
        date = (wb['Template'].cell(row=9, column=DATE_COL + col_adj).
            value.strftime('%Y%m%d'))

    return date, results

def parse_neuroreader_v2d2d8(pdf):
    """
    Parses neuroreader pdf files.

    **Paramters**

        pdf
            path to pdf file to convert
    **Outuputs**
        date
            The date of the exam. This if for file namimg purposes.
        results
            A dataframe. The columns are the measured variables the rows are
            participants. They should be identified by some random string so
            they are deidentified.
    """
    out_text = os.path.splitext(pdf)[0] + '.txt'

    pdftotext(pdf, out_text, '-table')

    with open(out_text) as in_file:
        lines = [x.strip().split() for x in in_file.readlines() if x.strip()]

    date = datetime.strptime(lines[1][5], '%Y-%b-%d').strftime('%Y%m%d')
    results = {
        'mTIV': float(lines[7][7]),
        'Hippocampus_Asym_Index': float(lines[9][0]),
        'Hippocampus_Asym_Zscor': float(lines[9][2]),
        'Hippocampus_Asym_percentile': float(lines[9][3]),
    }

    for line in lines[11:31] + lines[40:60]:
        structure = CLINICAL_NEUROREADER_MAPPER[''.join(line[0:len(line)-5])]
        results[structure + '_vol'] = float(line[-5])
        results[structure + '_TIVperc'] = float(line[-4])
        results[structure + '_Zscore'] = float(line[-2])
        results[structure + '_perc'] = float(line[-1])
    
    return date, pd.DataFrame(results)
    
    
    
