import os
import re
import sys
import json
import openpyxl

import pandas as pd
import PySimpleGUI as sg

from openpyxl.utils.exceptions import InvalidFileException

VARIABLE_TABLE_FILE = os.path.join('data', 'variable_table.json')
ALL_VARIABLES_FILE = os.path.join('data', 'all_variables.tsv')
GARBAGE = re.compile("^=|^raw$|^val$|^\[ERR\]$|^SS$")

def parse_neuroscore(variable_locs, file_path):
    """Parses variables from variable_locs in excel file file_path"""
    results = {'variable': [],
               'value': []}

    wb = openpyxl.load_workbook(file_path)
    for sheet_name, variables in variable_locs.items():
        sheet = wb[sheet_name]
        for variable, coordinate in variables.items():
            print('Reading variable {} at coordinate {}'.format(variable, coordinate))
            results['variable'].append(variable)
            value = sheet[coordinate].value
            if value is None or GARBAGE.match(value):
                value = ''
            results['value'].append(value)

    return results

def main():
    layout = [
        [sg.Text('Id', size=(10, 1), auto_size_text=False, justification='right'),
         sg.InputText(key='Participant')],
        [sg.Text('Source File', size=(10, 1), auto_size_text=False, justification='right'), 
         sg.InputText(key='InFile'), 
         sg.FileBrowse()],
        [sg.Submit(), sg.Cancel()]
    ]
    event, values = sg.Window('Neuroparser', layout, default_element_size=(40, 1)).Read()

    if event == "Submit":
        participant = values["Participant"]
        in_file = values["InFile"]

        with open(VARIABLE_TABLE_FILE) as variable_table_json:
            variable_table = json.load(variable_table_json)
        all_variables = pd.read_csv(ALL_VARIABLES_FILE, sep='\t')

        results = parse_neuroscore(variable_table, in_file)
        df = pd.DataFrame(results)
        out_data = (pd.merge(all_variables, df, how='left', on='variable')
                      .fillna({'value': ''})
                      .sort_values('number')
                      [['variable', 'value']])
        out_data['index'] = 0
        same_index = list(out_data.variable)
        out_data = (pd.pivot(out_data, index='index', 
                             columns='variable', values='value')
                      .reindex(same_index, axis=1))

        out_path = os.path.splitext(in_file)[0] + '.csv'
        out_data.to_csv(out_path)

if __name__ == '__main__':
    try:
        main()
    except FileNotFoundError as not_found:
        layout = [[sg.Text("File not found {}".format(not_found.filename), 
                   font=("Helvetica", 30))]]
        sg.Window('Neuroparser', layout).Read()
    except InvalidFileException as err:
        layout = [[sg.Text("{}".format(err), font=("Helvetica", 18))]]
        sg.Window('Neuroparser', layout).Read()
    except Exception as err:
        layout = [[sg.Text("Cannot handle error: {}".format(err), font=("Helvetica", 18))]]
        sg.Window('Neuroparser', layout).Read()
