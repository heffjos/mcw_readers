import os
import sys
import json
import openpyxl

import pandas as pd
import PySimpleGUI as sg

from openpyxl.utils.exceptions import InvalidFileException

from mcw_readers.parsers.clinical import parse_neuroscore

def gui():
    layout = [
        [sg.Text('record id', size=(22, 1), justification='left', auto_size_text=False),
         sg.InputText(key='record_id', default_text='', size=(15, None), enable_events=True)],
        [sg.Text('Neuroscore file', size=(22, 1), justification='left', auto_size_text=False), 
         sg.InputText(key='neuroscore', size=(23, None)), 
         sg.FileBrowse()],
        [sg.Text('redcap repeat instance', size=(22, 1), justification='left', auto_size_text=False),
         sg.InputText(key='i1', default_text='', size=(6, None), enable_events=True),
         sg.InputText(key='i2', default_text='', size=(6, None), enable_events=True),
         sg.InputText(key='i3', default_text='', size=(6, None), enable_events=True)],
        [sg.Submit(), sg.Cancel()]
    ]
    window = sg.Window('Parse Neuroscore', layout, default_element_size=(40, 1))

    while True:
        event, values = window.Read()
        if event == 'Submit':
            instances = {x: y for x, y in {0:'i1', 1:'i2', 2:'i3'}.items()
                         if len(values[y]) > 0}
            neuroscore_file = values['neuroscore']

            # check for duplicate instances
            check = set(instances.values())
            if len(check) < len(instances):
                raise Exception('Duplicated instaces.')

            # parse now
            results = []
            wb = openpyxl.load_workbook(neuroscore_file, read_only=True, data_only=True)
            for i, (exam, instance) in enumerate(instances.items()):
                sg.OneLineProgressMeter('', i, len(instances), 'key')
                df = parse_neuroscore(wb, exam)
                df['redcap_repeat_instance'] = values[instance]
                results.append(df)
            sg.OneLineProgressMeter('', len(instances), len(instances), 'key')

            out_file = os.path.splitext(neuroscore_file)[0] + '.csv'
            results = pd.concat(results)
            results['redcap_repeat_instrument'] = 'neuropsych_tests'
            results['record_id'] = int(values['record_id'])

            cols_to_order = ['record_id', 'redcap_repeat_instrument', 'redcap_repeat_instance']
            new_columns = cols_to_order + (results.columns.drop(cols_to_order).tolist())
            results = results[new_columns]

            results.to_csv(out_file, index=False)

            log_file = os.path.splitext(values['neuroscore'])[0] + '.json'
            with open(log_file, 'w') as f:
                json.dump(values, f, indent=4)

            break
        if event is None or event == 'Cancel':
            break

        for i in ['i1', 'i2', 'i3', 'record_id']:
            if values[i] != '' and values[i][-1] not in '0123456789':
                window.Element(i).Update(values[i][:-1])

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

if __name__ == "__main__":
    main()

