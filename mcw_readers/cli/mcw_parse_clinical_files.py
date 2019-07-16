import os
import sys
import openpyxl

import pandas as pd
import PySimpleGUI as sg

from openpyxl.utils.exceptions import InvalidFileException

def main():
    layout = [
        [sg.Text('Id', size=(20, 1), auto_size_text=False, justification='right'),
         sg.InputText(key='participant')],
        [sg.Text('Neuroscore runs', size=(20, 1), auto_size_text=False, justification='right'),
         sg.InputText(key='runs', default_text='1')],
        [sg.Text('Neuroscore file', size=(20, 1), auto_size_text=False, justification='right'), 
         sg.InputText(key='neuroscore_file'), 
         sg.FileBrowse()],
        [sg.Text('Neuroreader files:', size=(20, 1), auto_size_text=False, justification='right'), 
         sg.InputText(key='neuroreader_files'), 
         sg.FilesBrowse()],
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
