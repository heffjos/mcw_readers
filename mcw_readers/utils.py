import pandas as pd

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

from mcw_readers import data

def get_psychometric_objects():
    """converts the psychometric conversion table to a dict"""

    fname = 'psychometric_conversion_table_filled.csv'

    with pkg_resources.path(data, fname) as data_file:
        df = pd.read_csv(data_file.as_posix())

    results = {
        'standard_score': {},
        'scaled_score': {},
        'ets_score': {},
        't_score': {},
        'z_score': {},
        'description': {},
    }
    
    seen = set()
    for row in df.itertuples():
        pr = row.percentile_rank
    
        if pr in seen:
            results['standard_score'][pr].append(row.standard_score)
            results['scaled_score'][pr].append(row.scaled_score)
            results['ets_score'][pr].append(row.ets_score)
            results['t_score'][pr].append(row.t_score)
            results['z_score'][pr].append(row.z_score)
            results['description'][pr].append(row.description)
        else:
            results['standard_score'][pr] = [row.standard_score]
            results['scaled_score'][pr] = [row.scaled_score]
            results['ets_score'][pr] = [row.ets_score]
            results['t_score'][pr] = [row.t_score]
            results['z_score'][pr] = [row.z_score]
            results['description'][pr] = [row.description]
    
        seen.add(pr)

    return df, results

def close_any(value, test_values, close):
    """determines if any values in test_values are under close from value"""

    return any([abs(value - x) < close for x in test_values])

DF_PSYCHOMETRIC, DICT_PSYCHOMETRIC = get_psychometric_objects()
