import os
import re
import sys
import json

import pandas as pd

int_to_str = lambda x: x if pd.isnull(x) else '{:.0f}'.format(x)

data_dir = os.path.abspath('../data')
in_file = os.path.join(data_dir, 'comprehensive_sorted_neuropsych.xlsx')
out_file = os.path.join(data_dir, 'clinical_neuroscore_v3d0_variables.tsv')

# convert our excel file to an intelligent json for reading neuroscore
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
    out_file, sep='\t', index_label=False, float_format='%.0f')

