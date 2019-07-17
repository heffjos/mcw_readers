import os

import numpy as np
import pandas as pd

FIRST_DATA_ROW = 13 # contents = COGNITIVE STATUS

data_dir = os.path.abspath('../data')
in_file = os.path.join(data_dir, 'comprehensive_sorted_neuropsych.xlsx')
font_file = os.path.join(data_dir, 'neuroscore_3.0_font_properties.csv')
out_file = os.path.join(data_dir, 'clinical_neuroscore_v3d0_variables.tsv')

# we only want tp 1 or no timepoint variable names to match redcap 
# currently there are 975 of them
data = pd.read_excel(in_file, sheet_name='in')

included = data.loc[(data['tp'] == 1) | data['tp'].isnull(), :]
included['redcap'] = included['variable'].str.replace('_\d+$', '') 
included['column'] = included['column'].str.strip().apply(
    lambda x: x if pd.isnull(x) else ord(x.lower()) - 96)
included['column'] = included['column']
included['row'] = included['row']
included[['redcap', 'worksheet', 'row', 'column']].to_csv(
    out_file, sep='\t', index=False, float_format='%.0f')

# edit neurscore_3.0_font_properties
font_properties = pd.read_csv(font_file, sep='\t')
font_properties['row'] = range(FIRST_DATA_ROW, 
                              font_properties.shape[0] + FIRST_DATA_ROW)
font_properties['is_bold'][font_properties['is_bold'] == '#VALUE!'] = -1
font_properties['is_bold'] = font_properties['is_bold'].astype(int)
font_properties['is_bold'][font_properties['is_bold'] == -1] = 1
font_properties = font_properties[~ font_properties['measure'].isnull()]
font_properties['bold_header'] = [x if y else np.nan 
    for x, y in zip(font_properties['measure'], font_properties['is_bold'])]
font_properties['bold_header'] = font_properties['bold_header'].fillna(method='ffill')
loc_adjust_indent = font_properties['measure'].str.match('^\s')
font_properties['indent_level'][loc_adjust_indent] = (font_properties['indent_level'][loc_adjust_indent]
                                                      + 1)
indent_header = []
indent_reference = {}
for variable, cur_indent in zip(font_properties['measure'], 
                                font_properties['indent_level']):
    indent_reference[cur_indent] = variable
    if cur_indent == 0:
        indent_header.append(variable)
    else:
        indent_header.append(indent_reference[cur_indent - 1])
font_properties['indent_header'] = indent_header
        
    


                                  
