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

NEUROREADER_ECP_HEADER_MAPPER = {
    'Image ID': 'image_id',
    'Group name': 'group_name',
    'Study ID': 'study_id',
    'Clinical Image ID': 'clinical_image_id',
    'Patient ID': 'patient_id',
    'Gender': 'gender',
    # 'Analysis date': 'analysis_date', not grabbed from PyPDF4
    'Accession Number': 'accession_number',
    'Patient name': 'patient_name',
    'BirthDate': 'birth_date',
    'Age': 'age',
}

NEUROREADER_ECP_RESULTS_MAPPER = {
    'Hippocampal Left-Right Asymmetry Index': 'hippocampal_leftright_asymmetry_index',
    'NR Index': 'hippocampal_asymmetry_nr_index',
    'Z-score': 'hippocampal_asymmetry_zscore',
    'Percentile': 'hippocampal_asymmetry_percentile',
}

NEUROREADER_ECP_TABLE_MAPPER = {
    'Whole Brain Matter': 'whole_brain_matter',
    'Gray Matter': 'gray_matter',
    'White Matter': 'white_matter',
    'Hippocampus': 'hippocampus',
    'Right Hippocampus': 'right_hippocampus',
    'Left Hippocampus': 'left_hippocampus',
    'Amygdala': 'amygdala',
    'Right Amygdala': 'right_amygdala',
    'Left Amygdala': 'left_mygdatal',
    'Putamen': 'putamen',
    'Right Putamen': 'right_putamen',
    'Left Putamen': 'left_putamen',
    'Thalamus': 'thalamus',
    'Right Thalamus': 'right_thalamus',
    'Left Thalamus': 'left_thalamus',
    'Ventral Diencephalon': 'ventral_diencephalon',
    'Right Ventral Diencephalon': 'right_ventral_diencephalon',
    'Left Ventral Diencephalon': 'left_ventral_diencephalon',
    'Pallidum': 'pallidum',
    'Right Pallidum': 'right_pallidum',
    'Left Pallidum': 'left_pallidum',
    'Caudate': 'caudate',
    'Right Caudate': 'right_caudate',
    'Left Caudate': 'left_caudate',
    'Brain Stem': 'brain_stem',
    'Frontal Lobe': 'frontal_labe',
    'Right Frontal Lobe': 'right_frontal_lobe',
    'Left Frontal Lobe': 'left_frontal_lobe',
    'Parietal Lobe': 'parietal_lobe',
    'Right Parietal Lobe': 'right_parietal_lobe',
    'Left Parietal Lobe': 'left_parietal_lobe',
    'Occipital Lobe': 'occipictal_lobe',
    'Right Occipital Lobe': 'right_occipital_lobe',
    'Left Occipital Lobe': 'left_occiptial_lobe',
    'Temporal Lobe': 'temporal_lobe',
    'Right Temporal Lobe': 'right_temporal_lobe',
    'Left Temporal Lobe': 'left_temporal_lobe',
    'Cerebellum': 'cerebellum',
    'Right Cerebellum': 'right_cerebellum',
    'Left Cerebellum': 'left_cerebellum',
    'CSF (+ dura)': 'csf_plus_dura',
    'Lateral Ventricle': 'lateral_ventricle',
    'Right Lateral Ventricle': 'right_lateral_ventricle',
    'Left Lateral Ventricle': 'left_lateral_ventricle'
}

NEUROREADER_DEMENTIA_HEADER_MAPPER = {
    'Image ID': 'image_id',
    'Group name': 'group_name',
    'Study ID': 'study_id',
    'Clinical Image ID': 'clinical_image_id',
    'Patient ID': 'patient_id',
    'Gender': 'gender',
    # 'Analysis date': 'neuroreaderdate', not grabbed from PyPDF4
    'Accession Number': 'accession_number',
    'Patient name': 'patient_name',
    'BirthDate': 'birthdate',
    'Age': 'age',
}

NEUROREADER_DEMENTIA_RESULTS_MAPPER = {
    'Hippocampal Left-Right Asymmetry Index': 'Hippocampus_Asym_Index',
    'NR Index': 'nr_index',
    'Z-score': 'Hippocampus_Asym_Zscor',
    'Percentile': 'Hippocampus_Asym_percentile',
}

NEUROREADER_DEMENTIA_TABLE_MAPPER = {
    'Whole Brain Matter': 'WBV',
    'Gray Matter': 'GrayMatter',
    'White Matter': 'WhiteMatter',
    'Hippocampus': 'Hippocampus',
    'Right Hippocampus': 'Hippocampus_R',
    'Left Hippocampus': 'Hippocampus_L',
    'Amygdala': 'Amygdala',
    'Right Amygdala': 'Amygdala_R',
    'Left Amygdala': 'Amygdala_L',
    'Putamen': 'Putamen',
    'Right Putamen': 'Putamen_R',
    'Left Putamen': 'Putamen_L',
    'Thalamus': 'Thalamus',
    'Right Thalamus': 'Thalamus_R',
    'Left Thalamus': 'Thalamus_L',
    'Ventral Diencephalon': 'VentD',
    'Right Ventral Diencephalon': 'VentD_R',
    'Left Ventral Diencephalon': 'VentD_L',
    'Pallidum': 'Pallidum',
    'Right Pallidum': 'Pallidum_R',
    'Left Pallidum': 'Pallidum_L',
    'Caudate': 'Caudate',
    'Right Caudate': 'Caudate_R',
    'Left Caudate': 'Caudate_L',
    'Brain Stem': 'BrainStem',
    'Frontal Lobe': 'FrontalLobe',
    'Right Frontal Lobe': 'FrontalLobe_R',
    'Left Frontal Lobe': 'FrontalLobe_L',
    'Parietal Lobe': 'ParietalLobe',
    'Right Parietal Lobe': 'ParietalLobe_R',
    'Left Parietal Lobe': 'ParietalLobe_L',
    'Occipital Lobe': 'OccipitalLobe',
    'Right Occipital Lobe': 'OccipitalLobe_R',
    'Left Occipital Lobe': 'OccipitalLobe_L',
    'Temporal Lobe': 'TemporalLobe',
    'Right Temporal Lobe': 'TemporalLobe_R',
    'Left Temporal Lobe': 'TemporalLobe_L',
    'Cerebellum': 'Cerebellum',
    'Right Cerebellum': 'Cerebellum_R',
    'Left Cerebellum': 'Cerebellum_L',
}

NEUROREADER_MAPPERS = {
    'ECP': (NEUROREADER_ECP_HEADER_MAPPER,
            NEUROREADER_ECP_RESULTS_MAPPER,
            NEUROREADER_ECP_TABLE_MAPPER),
    'DEMENTIA': (NEUROREADER_DEMENTIA_HEADER_MAPPER,
                 NEUROREADER_DEMENTIA_RESULTS_MAPPER,
                 NEUROREADER_DEMENTIA_TABLE_MAPPER),
}

DF_PSYCHOMETRIC, DICT_PSYCHOMETRIC = get_psychometric_objects()
