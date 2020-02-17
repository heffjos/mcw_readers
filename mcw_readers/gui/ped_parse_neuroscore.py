import os
import sys
import json

import pandas as pd
import PySimpleGUI as sg

from pathlib import Path
from openpyxl.utils.exceptions import InvalidFileException

from mcw_readers.interfaces.lut import ped_lut
from mcw_readers.interfaces.wb_parsers import peds_wb_parser

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

from .. import data

def gui(file_ped_lut=None):
    layout = [
        [sg.Text('record id', size=(22, 1), justification='left', auto_size_text=False),
         sg.InputText(key='record_id', default_text='', size=(15, None), enable_events=True)],
        [sg.Text('Neuroscore file', size=(22, 1), justification='left', auto_size_text=False), 
         sg.InputText(key='neuroscore', size=(23, None)), 
         sg.FileBrowse()],
        [sg.Submit(), sg.Cancel()]
    ]
    window = sg.Window('Parse ped neuroscore', layout, default_element_size=(40, 1))

    while True:
        event, values = window.Read()
        if event == 'Submit':
            file_neuroscore = Path(values['neuroscore'])
            out_dir = file_neuroscore.parent
            out_file_redcap = out_dir.joinpath(file_neuroscore.stem + 
                                               '_REDCAP.csv')
            out_file_new_identifiers = out_dir.joinpath(file_neuroscore.stem + 
                                                        '_NEW_IDENTIFIERS.csv')
            out_file_log = out_dir.joinpath(file_neuroscore.stem +
                                            '_LOG.json')
            
            # parse now
            if file_ped_lut:
                current_lut = ped_lut(file_ped_lut)
            else:
                with pkg_resources.path(data, 'ped_lut.xlsx') as data_file:
                    current_lut = ped_lut(data_file)

            peds_parser = peds_wb_parser(file_neuroscore)
            data, new_identifiers = peds_parser.parse_data(current_lut)
            data['record_id'] = int(values['record_id'])

            df_data = pd.DataFrame(data, index=[0])
            df_data = df_data[['record_id'] + 
                              df_data.columns.drop(['record_id']).tolist()]
            df_data.to_csv(out_file_redcap, index=False)

            df_new_identifiers = pd.DataFrame(new_identifiers)
            df_new_identifiers.to_csv(out_file_new_identifiers, index=False)

            with open(out_file_log, 'w') as f:
                json.dump(values, f, indent=4)

            break
        if event is None or event == 'Cancel':
            break

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

if __name__ == "__main__":
    main()

