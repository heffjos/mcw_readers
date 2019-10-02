import os
import re

import numpy as np
import pandas as pd

from datetime import datetime

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

from .. import data
from ..utils import (
    pdftotext, clinical_detect_neuroscore_version, CLINICAL_NEUROREADER_MAPPER
)

with pkg_resources.path(data, 'clinical_redcap_labeled.tsv') as data_file:
    CLINICAL_VARIABLES = pd.read_csv(data_file, sep='\t')

with pkg_resources.path(data, 'clinical_neuropsych_tests.tsv') as data_file:
    CLINICAL_TESTS = pd.read_csv(data_file, sep='\t')
UNIQUE_TESTS = list(pd.unique(CLINICAL_TESTS['test']))

DATE_COL = 5

def parse_neuroscore(wb, exam, debug=False):
    """
    Parses neuroscore workbook, primarily the Template worksheet.

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
        results
            A dataframe. The columns are the measured variables. The rows are
            participants. The presence of subtests are added to match the 
            redcap import tool csv file.
    """
    col_adj = exam * 4
    version = clinical_detect_neuroscore_version(wb)
    if version == None:
        raise Exception('Could not detect clinical neuroscore version')

    df_key = CLINICAL_VARIABLES[CLINICAL_VARIABLES['version'] == version].copy()
    df_key['column'] = df_key['column'] + col_adj

    worksheets = pd.unique(df_key['worksheet'])
    if any(pd.isnull(worksheets)):
        raise Exception('There are unassigned worksheets in {}'.format(data_file))

    results = {'variable': [], 'value': []}
    # missing assigments have no group value
    for ws, df in df_key.groupby('worksheet'):
        sheet = wb[ws]

        values = [sheet.cell(row=int(x), column=int(y)).value
                  for x, y in zip(df['row'], df['column'])]

        results['variable'].extend(list(df['redcap']))
        results['value'].extend(values)

    results['variable'].append('np_date')
    if debug:
        results['value'].append('07071977')
    else:
        results['value'].append(wb['Template']
                                .cell(row=9, column=DATE_COL + col_adj)
                                .value
                                .strftime('%Y-%m-%d'))

    results = pd.DataFrame(results).fillna(pd.np.nan)

    garbage = results['value'].str.match(r'^=|^raw$|^val$|^\[ERR\]$|^SS$', 
                                         na=False)
    results['value'][garbage] = pd.np.nan

    tests_check = CLINICAL_TESTS.merge(results, 
                                       how='left', 
                                       left_on='redcap', 
                                       right_on='variable')
    tests_check['check'] = tests_check['value'].notna()
    tests_check = (tests_check
                   .groupby('test')
                   .agg({'check': pd.np.sum})
                   .reset_index())
    tests_check.rename(columns={'test': 'variable', 'check': 'value'}, inplace=True)
    tests_check['value'][tests_check['value'] > 0] = 1

    results = pd.concat((results, tests_check))

    results['index'] = 0
    results = results.pivot(index='index', columns='variable', values='value')
        
    return results

def parse_neuroreader_v2d2d8(pdf):
    """
    Parses neuroreader pdf files.

    **Paramters**

        pdf
            path to pdf file to convert
    **Outuputs**
        results
            A dataframe. The columns are the measured variables the rows are
            participants. They should be identified by some random string so
            they are deidentified.
    """
    out_text = os.path.splitext(pdf)[0] + '.txt'

    pdftotext(pdf, out_text, '-table')

    with open(out_text) as in_file:
        lines = [x.strip().split() for x in in_file.readlines() if x.strip()]

    results = {
        'image_id': lines[0][2],
        'group_name': lines[1][2], 
        'neuroreaderdate': datetime.strptime(lines[1][5], '%Y-%b-%d').strftime('%Y-%m-%d'),
        'study_id': int(lines[2][2]),
        'acession_number': lines[2][5],
        'clinical_image_id': lines[3][3],
        'patient_id': lines[4][2],
        'first_name': lines[4][5],
        'last_name': lines[4][6],
        'gender': lines[5][1],
        'birthdate': datetime.strptime(lines[5][3], '%m-%d-%Y').strftime('%Y-%m-%d'),
        'version': lines[-1][-1],

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

    return pd.DataFrame(results, index=[0])
    
