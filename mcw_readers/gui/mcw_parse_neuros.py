import os
import sys
import json
import openpyxl

import pandas as pd
import PySimpleGUI as sg

from openpyxl.utils.exceptions import InvalidFileException

from mcw_readers.parsers.clinical import (
    parse_neuroscore, parse_neuroreader_v2d2d8)

def main():
    layout = [
        [sg.Text('Id', size=(15, 1), auto_size_text=False, justification='right'),
         sg.InputText(key='participant')],
        [sg.Text('Neuroscore tp 1', size=(15, 1), auto_size_text=False, justification='right'),
         sg.Input(key='tp1', default_text='', size=(6, None), enable_events=True),
         sg.Text('Neuroreader tp 1'),
         sg.InputText(key='neuroreader1'),
         sg.FileBrowse()],
        [sg.Text('Neuroscore tp 2', size=(15, 1), auto_size_text=False, justification='right'),
         sg.InputText(key='tp2', default_text='', size=(6, None), enable_events=True),
         sg.Text('Neuroreader tp 2'),
         sg.InputText(key='neuroreader2'),
         sg.FileBrowse()],
        [sg.Text('Neuroscore tp 3', size=(15, 1), auto_size_text=False, justification='right'),
         sg.InputText(key='tp3', default_text='', size=(6, None), enable_events=True),
         sg.Text('Neuroreader tp 3'),
         sg.InputText(key='neuroreader3'),
         sg.FileBrowse()],
        [sg.Text('Neuroscore file', size=(15, 1), auto_size_text=False, justification='right'), 
         sg.InputText(key='neuroscore'), 
         sg.FileBrowse()],
        [sg.Submit(), sg.Cancel()]
    ]
    window = sg.Window('Clinical Parse', layout, default_element_size=(40, 1))

    while True:
        event, values = window.Read()
        if event == 'Submit':
            participant = values['participant']
            run_vars = ['tp' + str(x) for x in [1, 2, 3]]
            neuroreader_vars = ['neuroreader' + str(y) for y in [1, 2, 3]]
            runs = [values[x] for x in run_vars]
            neuroreaders = [values[x] for x in neuroreader_vars]
            neuroscore_file = values['neuroscore']

            # check all neuroreader_files have a run
            pairs = []
            for run, neuroreader in zip(runs, neuroreaders):
                if neuroreader and not run:
                    raise Exception('Undefined run for neuroreader_file: '
                                    '{}'.format(pair[1]))
                if run:
                    if neuroreader:
                        pairs.append((run, neuroreader))
                    else:
                        pairs.append((run, None))

            # parse now
            results = []
            wb = openpyxl.load_workbook(neuroscore_file, read_only=True, data_only=True)
            for i, pair in enumerate(pairs):
                df = parse_neuroscore(wb, i)
                if pair[1]:
                    neuroreader_df = parse_neuroreader_v2d2d8(pair[1])
                    df[neuroreader_df.columns] = neuroreader_df.iloc[0, :].values

                df['id'] = values['participant']
                results.append(df)
            out_file = os.path.splitext(neuroscore_file)[0] + '.csv'
            pd.concat(results).to_csv(out_file, index=False)

            log_file = os.path.splitext(values['neuroscore'])[0] + '.json'
            with open(log_file, 'w') as f:
                json.dump(values, f, indent=4)

            break
        if event is None or event == 'Cancel':
            break
        for tp in ['tp1', 'tp2', 'tp3']:
            if values[tp] != '' and values[tp][-1] not in '0123456789':
                window.Element(tp).Update(values[tp][:-1])

    window.Close()

if __name__ == '__main__':
    try:
        main()
    except FileNotFoundError as not_found:
        sg.PopupError('File not found {}'.format(not_found.filename))
    except InvalidFileException as err:
        sg.PopupError('{}'.format(err))
    except Exception as err:
        sg.PopupError('Unhandled error: {}\n'
                      'Email help: jheffernan@mcw.edu'.format(err))
