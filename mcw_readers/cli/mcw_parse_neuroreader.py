import os
import sys

import pandas as pd
import PySimpleGUI as sg

sys.path.insert(0, '/home/heffjos/Documents/Work/repositories/mcw_readers')

from mcw_readers.parsers.clinical import parse_neuroreader_v2d2d8

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

def main():
    with pkg_resources.path('mcw_readers.data', 'clinical_versions_labeled.tsv') as data_file:
        variables = pd.read_csv(data_file, sep='\t')
        variables = variables[variables['version'] == '3.0ulatest']
        results = pd.DataFrame({x: [np.nan] for x in variables['redcap'])
        

    layout = [
        [sg.Text('Id', size=(15, 1), auto_size_text=False, justification='right'),
         sg.InputText(key='participant')],
        [sg.Text('Timepoint', size=(15, 1), auto_size_text=False, justification='right'),
         sg.Input(key='timepoint', default_text='', size=(6, None), enable_events=True),
         sg.Text('Neuroreader'),
         sg.InputText(key='neuroreader'),
         sg.FileBrowse()],
        [sg.Submit(), sg.Cancel()]
    ]
    window = sg.Window('Neuroreader', layout, default_element_size=(40, 1))

    while True:
        event, values = window.Read()
        if event == 'Submit':
            date, df = parse_neuroreader_v2d2d8(values['neuroreader'])
            df['date'] = date
            df['id'] = values['participant']
            out_file = os.path.splitext(pdf)[0] + '.csv'
            
            # TODO: Combine these with missing values of neuroscore
            df.to_csv(out_file, index=False)
            break
        if event is None or event == 'Cancel':
            break
        if values['timepoint'] != '' and values['timepoint'][-1] not in '0123456789':
            window.Element('timepoint').Update(values['timepoint'][:-1])

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

        
