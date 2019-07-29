import os
import sys
import openpyxl

import pandas as pd
import PySimpleGUI as sg

from openpyxl.utils.exceptions import InvalidFileException

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
         sg.InputText(key='neuroscore_file'), 
         sg.FileBrowse()],
        [sg.Submit(), sg.Cancel()]
    ]
    window = sg.Window('Clinical Parse', layout, default_element_size=(40, 1))

    while True:
        event, values = window.Read()
        if event == 'Submit':
            participant = values['participant']
            runs = values['runs']
            neuroscore_file = values['neuroscore_file']
            neuroreader_files = values['neuroreader_files']

            sg.Popup('Participant      : {}\n'
                     'Runs             : {}\n'
                     'Neuroscore file  : {}\n'
                     'Neuroreader files: {}\n'.format(participant,
                                                    runs,
                                                    neuroscore_file,
                                                neuroreader_files))
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
