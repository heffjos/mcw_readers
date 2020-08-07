import os
import re

import pandas as pd
import PyPDF4 as pdf

from datetime import datetime

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

# from .. import data
from ..utils import NEUROREADER_MAPPERS

# with pkg_resources.path(data, 'clinical_redcap_labeled.tsv') as data_file:
#     CLINICAL_VARIABLES = pd.read_csv(data_file, sep='\t')
# 
# with pkg_resources.path(data, 'clinical_neuropsych_tests.tsv') as data_file:
#     CLINICAL_TESTS = pd.read_csv(data_file, sep='\t')
# UNIQUE_TESTS = list(pd.unique(CLINICAL_TESTS['test']))
# 
# DATE_COL = 5
# 
# def parse_neuroscore(wb, exam, debug=False):
#     """
#     Parses neuroscore workbook, primarily the Template worksheet.
# 
#     **Parameters**
# 
#         wb
#             an openpyxl workbook, speed is greatly improved when 
#             read_only=True and maybe data_only=True
#         exam
#             The template worksheet has up to 3 visits (known as exames in the)
#             worksheet) data sets. This controls which exam is parsed. 
#             It is ***zero-based*** indexing.
#         debug
#             This controls whether to parse the exam date. It allows for testing
#             without setting the date.
# 
#     **Outputs**
#         results
#             A dataframe. The columns are the measured variables. The rows are
#             participants. The presence of subtests are added to match the 
#             redcap import tool csv file.
#     """
#     col_adj = exam * 4
#     version = clinical_detect_neuroscore_version(wb)
#     if version == None:
#         raise Exception('Could not detect clinical neuroscore version')
# 
#     df_key = CLINICAL_VARIABLES[CLINICAL_VARIABLES['version'] == version].copy()
#     df_key['column'] = df_key['column'] + col_adj
# 
#     worksheets = pd.unique(df_key['worksheet'])
#     if any(pd.isnull(worksheets)):
#         raise Exception('There are unassigned worksheets in {}'.format(data_file))
# 
#     results = {'variable': [], 'value': []}
#     # missing assigments have no group value
#     for ws, df in df_key.groupby('worksheet'):
#         sheet = wb[ws]
# 
#         values = [sheet.cell(row=int(x), column=int(y)).value
#                   for x, y in zip(df['row'], df['column'])]
# 
#         results['variable'].extend(list(df['redcap']))
#         results['value'].extend(values)
# 
#     results['variable'].append('np_date')
#     if debug:
#         results['value'].append('07071977')
#     else:
#         results['value'].append(wb['Template']
#                                 .cell(row=9, column=DATE_COL + col_adj)
#                                 .value
#                                 .strftime('%Y-%m-%d'))
# 
#     results = pd.DataFrame(results).fillna(pd.np.nan)
# 
#     garbage = results['value'].str.match(r'^=|^raw$|^val$|^\[ERR\]$|^SS$', 
#                                          na=False)
#     results['value'][garbage] = pd.np.nan
# 
#     tests_check = CLINICAL_TESTS.merge(results, 
#                                        how='left', 
#                                        left_on='redcap', 
#                                        right_on='variable')
#     tests_check['check'] = tests_check['value'].notna()
#     tests_check = (tests_check
#                    .groupby('test')
#                    .agg({'check': pd.np.sum})
#                    .reset_index())
#     tests_check.rename(columns={'test': 'variable', 'check': 'value'}, inplace=True)
#     tests_check['value'][tests_check['value'] > 0] = 1
# 
#     results = pd.concat((results, tests_check))
# 
#     results['index'] = 0
#     results = results.pivot(index='index', columns='variable', values='value')
# 
#     # convert results here
#     results['gds_class'] = results['gds_class'].map({'WNL': 0,
#                                                      'Mild': 1,
#                                                      'Mod': 2,
#                                                      'Sev': 3})
#     results['hvlt_delay_ss'] = results['hvlt_delay_ss'].str.replace('^<', '')
#     results['hvlt_disc_ss'] = results['hvlt_delay_ss'].str.replace('^<', '')
#     results['hvlt_perc_ss'] = results['hvlt_perc_ss'].str.replace('^<', '')
#     results['trailsa_err'] = results['trailsa_err'].str.replace('-E$', '')
#     results['trailsb_err'] = results['trailsb_err'].str.replace('-E$', '')
#     results['wcst_cat_perc'] = results['wcst_cat_perc'].map({'[<1]': 0,
#                                                              '[2-5]': 1,
#                                                              '[6-10]': 2,
#                                                              '[11-16]': 3,
#                                                              '[>16]': 4})
#     results['wcst_fms_perc'] = results['wcst_fms_perc'].map({'[<1]': 0,
#                                                              '[2-5]': 1,
#                                                              '[6-10]': 2,
#                                                              '[11-16]': 3,
#                                                              '[>16]': 4})
#     results['wms_io_per'] = results['wms_io_per'].str.extract('^\[(\d+)\]')
#         
#     return results

def get_field_locs(working_data, fields):
    """
    Finds fields index locations.

    Parameters
    ----------

    working_data: list-like
        the working data
    fields: list-like
        the field names

    Outputs
    -------

    field_locs: dict
        field-index pairs
    """

    field_locs = {x:i for i,x in enumerate(working_data) if x in fields}

    not_found = set(fields) - set(field_locs)
    if not_found:
        raise Exception(f'Missing fields {not_found}')

    return field_locs
        

def parser_neuroreader(pdf_file, study):
    """
    Parses neuroreader files.

    Parameters
    ----------

    pdf_file: str
        path to pdf file
    study: str
        study name which determines how pdf names are mapped to DataFrame columns

    Outputs
    -------

    results: pd.DataFrame
        The columns are the measured variables, the rows are participants.
    """

    mtiv_field = 'The measured total intracranial volume'
    mtiv_loc = 22

    header_mapper = NEUROREADER_MAPPERS[study][0]
    results_mapper = NEUROREADER_MAPPERS[study][1]
    table_mapper = NEUROREADER_MAPPERS[study][2]

    pdf_data = {}
    with open(pdf_file, 'rb') as f:
        pdf_fr = pdf.PdfFileReader(f)
        n = pdf_fr.getNumPages()

        for i in range(n):
            pdf_data[i] = pdf_fr.getPage(i).extractText().strip().split('\n')
        info = pdf_fr.getDocumentInfo()

    results = {}

    if header_mapper is not None:
        working_data = pdf_data[0]
        field_locs = get_field_locs(working_data, header_mapper)

        for field, loc in field_locs.items():
            results[header_mapper[field]] = working_data[loc + 1]

    if results_mapper is not None:
        working_data = pdf_data[0]
        field_locs = get_field_locs(working_data, results_mapper)

        for field, loc in field_locs.items():
            results[results_mapper[field]] = float(working_data[loc + 4])

    if table_mapper is not None:
        working_data = pdf_data[0] + pdf_data[1]
        field_locs = get_field_locs(working_data, table_mapper)

        for field, loc in field_locs.items():
            study_field = table_mapper[field]
            results[study_field + '_vol_ml'] = float(working_data[loc + 1])
            results[study_field + '_vol_to_tiv_ratio'] = float(working_data[loc + 2])
            results[study_field + '_nr_index'] = float(working_data[loc + 3])
            results[study_field + '_zscore'] = float(working_data[loc + 4])
            results[study_field + '_percentile'] = float(working_data[loc + 5])

    results['version'] = pdf_data[0][-1]

    # get mitv
    if not pdf_data[0][mtiv_loc].startswith(mtiv_field):
        for i, field in enumerate(pdf_data[0]):
            if field.startswith(mtiv_field):
                mtiv_loc = i
                break

    ptn = 'The measured total intracranial volume \(mTIV\) = (\d+) ml.'
    results['mtiv'] = float(re.search(ptn, pdf_data[0][mtiv_loc]).group(1))

    # split patient name
    patient_names = results[header_mapper['Patient name']].split()
    results['first_name'] = patient_names[1]
    results['last_name'] = patient_names[0]
    if len(patient_names) >= 3:
        results['middle_name'] = patient_names[2]
    results.pop(header_mapper['Patient name'])

    # format birthdate
    birthdate = results[header_mapper['BirthDate']]
    results[header_mapper['BirthDate']] = (datetime
        .strptime(birthdate, '%m-%d-%Y')
        .strftime('%Y-%m-%d'))

    # perfom study specific operations
    analysis_date = results[header_mapper['Image ID']].split('_')[1]

    if study == 'DEMENTIA':
        results['neuroreaderdata'] = (datetime
            .strptime(analysis_date, '%Y%m%d%H%M%S')
            .strftime('%Y-%m-%d'))

        results.pop('middle_name')

    elif study == 'ECP':
        results['analysis_date'] = (datetime
            .strptime(analysis_date, '%Y%m%d%H%M%S')
            .strftime('%Y-%m-%d %H:%M:%S'))

    return pd.DataFrame(results, index=[0])
    
