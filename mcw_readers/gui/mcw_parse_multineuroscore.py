import os
import sys
import json
import errno
import openpyxl

import pandas as pd
import PySimpleGUI as sg

from openpyxl.utils.exceptions import InvalidFileException

from mcw_readers.parsers.clinical import parse_neuroscore

HEADER = pd.Series(['record_id', 'neuroscore', 'exam', 'redcap_repeat_instance'])

def validate_tsv(tsv):
    df = pd.read_csv(tsv, 
                     sep='\t',
                     dtype={'record_id': pd.np.int,
                            'neuroscore': str,
                            'exam': pd.np.int,
                            'redcap_repeat_instance': pd.np.int})

    header_check = df.columns.isin(HEADER)
    if not all(header_check):
        raise Exception(f'Missing columns: {HEADER[~header_check].to_list()}')

    for neuroscore_file in df['neuroscore']:
        if not os.path.isfile(neuroscore_file):
            raise FileNotFoundError(errno.ENOENT, 
                                    os.strerror(errno.ENOENT), 
                                    neuroscore_file)

    for exam in df['exam']:
        if exam > 3:
            raise Exception(f'Found exam number {exam}. Expected 1, 2, or 3')

    return df

def gui():
    layout = [
        [sg.Text('Tab delimited file', size=(22, 1), justification='left', auto_size_text=False), 
         sg.InputText(key='tsv_file', size=(23, None)), 
         sg.FileBrowse()],
        [sg.Submit(), sg.Cancel()]
    ]
    window = sg.Window('Parse Neuroscore', layout, default_element_size=(40, 1))

    while True:
        event, values = window.Read()
        if event == 'Submit':
            tsv_file = values['tsv_file']

            tsv_df = validate_tsv(tsv_file)

            results = []
            for i, row in enumerate(tsv_df.itertuples(index=False)):
                wb = openpyxl.load_workbook(row.neuroscore, read_only=True, data_only=True)
                sg.OneLineProgressMeter('', i, tsv_df.shape[0], 'key')
                df = parse_neuroscore(wb, row.exam - 1)
                df['redcap_repeat_instance'] = row.redcap_repeat_instance
                df['record_id'] = row.record_id
                results.append(df)
            sg.OneLineProgressMeter('', tsv_df.shape[0], tsv_df.shape[0], 'key')

            results = pd.concat(results)
            results['redcap_repeat_instrument'] = 'neuropsych_tests'

            cols_to_order = ['record_id', 'redcap_repeat_instrument', 'redcap_repeat_instance']
            new_columns = cols_to_order + (results.columns.drop(cols_to_order).tolist())
            results = results[new_columns]

            out_dir = os.path.dirname(values['tsv_file'])
            out_fname = 'out_' + os.path.basename(values['tsv_file'])
            out_file = os.path.join(out_dir, out_fname)

            results.to_csv(out_file, index=False)
            
            break

        if event is None or event == 'Cancel':
            break

    window.Close()

def main():
    try:
        gui()
    except FileNotFoundError as not_found:
        sg.PopupError(f'File not found {not_found.filename}', title='ERROR')
    except InvalidFileException as err:
        sg.PopupError(f'{err}', title='ERROR')
    except Exception as err:
        sg.PopupError(f'Unhandled error: {err}\n\n'
                      'Email help: jheffernan@mcw.edu',
                      title='ERROR')

if __name__ == '__main__':
    main()
