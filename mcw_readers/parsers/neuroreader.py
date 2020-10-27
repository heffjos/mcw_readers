import os
import re

import pandas as pd
import PyPDF4 as pdf

from datetime import datetime

from ..utils import NEUROREADER_MAPPERS

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
        
def parse_neuroreader(pdf_file, study):
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
    
