import pandas as pd

df = pd.read_csv('/home/jheffernan/test.tsv', sep='\t', na_values=['', ' '])
redcap_variables = pd.read_csv('../data/clinical_redcap_variables.tsv', sep='\t')
redcap_variables = pd.DataFrame(columns=redcap_variables['redcap'])

melted_df = pd.melt(df.reset_index(), id_vars=['index'])

melted_df['tp'] = (melted_df['variable']
                   .str.extract(r'_(\d|[bB][lL])$', expand=False)
                   .str.lower())
melted_df['tp'][melted_df['tp'].isnull()] = 'no_tp'

melted_df['base'] = (melted_df['variable']
                     .str.replace(r'_(\d|[bB][lL])$', '')
                     .str.lower())

base_count = melted_df.groupby(['tp', 'base']).count().reset_index()
all_column_names = {key: set(base_count[base_count['tp'] == key]['base'])
                    for key in pd.unique(base_count['tp'])}
all_intersecting_columns = {key: value.intersection(all_column_names['no_tp'])
                            for key, value in all_column_names.items()
                            if key != 'no_tp'}


no_null_melted = melted_df[~melted_df['value'].isnull()]
melted_dfs = {x: no_null_melted[no_null_melted['tp'] == x]
              for x in pd.unique(no_null_melted['tp'])}
wide_dfs = {key: value.pivot(index='index', columns='base', values='value') 
            for key, value in melted_dfs.items()}

tp_dfs = {key: value for key, value in wide_dfs.items() if key != 'no_tp'}
column_names = {key: set(value.columns) for key, value in wide_dfs.items()}
intersecting_columns = {key: value.intersection(column_names['no_tp'])
                        for key, value in column_names.items()
                        if key != 'no_tp'}

# final_dfs = []
# for tp, tp_df in wide_dfs.items():
#     if tp != 'no_tp':
#         final_df = tp_df.join(wide_dfs['no_tp'])
#         final_df['tp'] = tp
#         final_dfs.append(pd.concat((redcap_variables, final_df)))
    

quick_count = {key: value.dropna(how='all').shape
               for key, value in wide_dfs.items()}

dates = {key: value.columns[value.columns.str.contains(r'date') 
                            & ~value.columns.str.contains(r'caudate')]
         for key, value in wide_dfs.items()}
