import pandas as pd

from pathlib import Path
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from mcw_readers.interfaces.lut import lut
from mcw_readers.interfaces.wb_parsers import wb_parser

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

def get_parser():
    """get cli parse"""

    parser_desc = 'parse multiple neuroscores as defined by a spec file'
    epilog = """
The spec file is a tsv. Each line represents a timepoint for a participant. 
The timepoints must be matched with the exams (A, B, or C) in neuroscore.
Here are the tsv columns names and the information they represent:
    record_id
        The redcap record_id for the participant.
    redcap_repeat_instance
        The redcap repeat instance.
    neuroscore
        The full path to the Neuroscore xlsm file.
    exam
        The exam (A, B, or C) matching with the redcap_repeat_instance
"""
        
    parser = ArgumentParser(description=parser_desc, 
                            formatter_class=RawDescriptionHelpFormatter,
                            epilog=epilog)
    parser.add_argument('--spec', action='store', required=True,
                        help='the tsv specification')

    return parser

def main():
    with pkg_resources.path('mcw_readers.data', 
                            'epilepsy_lut.xlsx') as epilepsy_excel:
        epilepsy_lut = lut('epilepsy', str(epilepsy_excel))
        
    parser = get_parser()
    args = parser.parse_args()

    spec = pd.read_csv(args.spec, sep='\t')
    spec.exam = spec.exam.str.lower()
    spec['exam_num'] = spec.exam.map({'a': 1, 'b': 2})
    N = spec.shape[0]

    all_results = []
    all_new_lines = []
    all_missing_lines = []
    for i, row in enumerate(spec.itertuples(), start=1):
        print(f'Working on row {i} / {N}')

        epilepsy_parser = wb_parser(row.neuroscore, verbose=False)
        results, new_lines, missing_lines = epilepsy_parser.parse_data(
            epilepsy_lut, row.exam_num) 

        # adjust results
        results = pd.DataFrame(results)

        results['record_id'] = row.record_id
        results['redcap_repeat_instrument'] = 'neuropsych_testing'
        results['redcap_repeat_instance'] = row.redcap_repeat_instance

        cols = ['record_id', 
                'redcap_repeat_instrument', 
                'redcap_repeat_instance']
        cols = cols + [col for col in results if col not in cols]
        results = results[cols]

        # adjust new lines
        if new_lines:
            new_lines = pd.DataFrame(new_lines)
            N_new_lines = new_lines.shape[0]
            print(f'Found {N_new_lines} new lines.')

            new_lines['record_id'] = row.record_id
            new_lines['redcap_repeat_instance'] = row.redcap_repeat_instance
            new_lines['neuroscore'] = row.neuroscore
            new_lines['exam'] = row.exam

            cols = ['record_id',
                    'redcap_repeat_instance',
                    'neuroscore',
                    'exam']
            cols = cols + [col for col in new_lines if col not in cols]
            new_lines = new_lines[cols]

            all_new_lines.append(new_lines)

        # adjust missing_lines
        if missing_lines:
            missing_lines = pd.DataFrame(missing_lines)
            N_missing_lines = missing_lines.shape[0]
            print(f'Found {N_missing_lines} missing lines.')

            missing_lines['record_id'] = row.record_id
            missing_lines['redcap_repeat_instance'] = row.redcap_repeat_instance
            missing_lines['neuroscore'] = row.neuroscore
            missing_lines['exam'] = row.exam
       
            cols = ['record_id',
                    'redcap_repeat_instance',
                    'neuroscore',
                    'exam']
            cols = cols + [col for col in missing_lines if col not in cols]
            missing_lines = missing_lines[cols]

            all_missing_lines.append(missing_lines)

        all_results.append(results)

    # handle output
    spec_file = Path(args.spec)
    out_dir = spec_file.parent
    stem = spec_file.stem
    results_file = out_dir.joinpath(f'{stem}_redcap.csv')
    new_lines_file = out_dir.joinpath(f'{stem}_new_lines.csv')
    missing_lines_file = out_dir.joinpath(f'{stem}_missing_lines.csv')

    all_results = pd.concat(all_results).reset_index(drop=True)
    all_results.to_csv(results_file, float_format='%.6g', index=False)

    if all_new_lines:
        all_new_lines = pd.concat(all_new_lines).reset_index(drop=True)
        all_new_lines.to_csv(
            new_lines_file, float_format='%.6g', index=False)

    if all_missing_lines:
        all_missing_lines = pd.concat(all_missing_lines).reset_index(drop=True)
        all_missing_lines.to_csv(
            missing_lines_file, float_format='%.6g', index=False)

if __name__ == '__main__':
    main()
