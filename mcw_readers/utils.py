import sys
import subprocess

import pandas as pd

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

from . import data

def clinical_build_version_key():
    version_key = {}
    with pkg_resources.path(data, 'clinical_version_key.tsv') as key_file:
        df = pd.read_csv(key_file, sep='\t')

    df['rc'] = list(zip(df['row'], df['column']))
    versions = set(pd.unique(df['version']))
    versions.difference({'3.0u2.30', '3.0u11.01.16'})
    for version in versions:
        version_df = df[df['version'] == version]
        version_key[version] = {x: y if not pd.isnull(y) else None 
                                for x, y in zip(version_df['rc'], 
                                                version_df['measure'])}

    return version_key

CLINICAL_NEUROSCORE_VERSIONS_IDENTIFIERS = clinical_build_version_key()

CLINICAL_NEUROREADER_MAPPER = {
    'WholeBrainMatter': 'WBV',
    'GrayMatter': 'GrayMatter',
    'WhiteMatter': 'WhiteMatter',
    'Hippocampus': 'Hippocampus',
    'RightHippocampus': 'Hippocampus_R',
    'LeftHippocampus': 'Hippocampus_L',
    'Amygdala': 'Amygdala',
    'RightAmygdala': 'Amygdala_R',
    'LeftAmygdala': 'Amygdala_L',
    'Putamen': 'Putamen',
    'RightPutamen': 'Putamen_R',
    'LeftPutamen': 'Putamen_L',
    'Thalamus': 'Thalamus',
    'RightThalamus': 'Thalamus_R',
    'LeftThalamus': 'Thalamus_L',
    'VentralDiencephalon': 'VentD',
    'RightVentralDiencephalon': 'VentD_R',
    'LeftVentralDiencephalon': 'VentD_L',
    'Pallidum': 'Pallidum',
    'RightPallidum': 'Pallidum_R',
    'LeftPallidum': 'Pallidum_L',
    'Caudate': 'Caudate',
    'RightCaudate': 'Caudate_R',
    'LeftCaudate': 'Caudate_L',
    'BrainStem': 'BrainStem',
    'FrontalLobe': 'FrontalLobe',
    'RightFrontalLobe': 'FrontalLobe_R',
    'LeftFrontalLobe': 'FrontalLobe_L',
    'ParietalLobe': 'ParietalLobe',
    'RightParietalLobe': 'ParietalLobe_R',
    'LeftParietalLobe': 'ParietalLobe_L',
    'OccipitalLobe': 'OccipitalLobe',
    'RightOccipitalLobe': 'OccipitalLobe_R',
    'LeftOccipitalLobe': 'OccipitalLobe_L',
    'TemporalLobe': 'TemporalLobe',
    'RightTemporalLobe': 'TemporalLobe_R',
    'LeftTemporalLobe': 'TemporalLobe_L',
    'Cerebellum': 'Cerebellum',
    'RightCerebellum': 'Cerebellum_R',
    'LeftCerebellum': 'Cerebellum_L',
}

def pdftotext(in_pdf, out_text, options=None):
    """
    Converts pdf files to text files

    **Parameters**

        in_pdf
            Path to pdf for converions
        out_text
            the output text file from conversion
        options
            a string noting the options to give binary `pdftotext`
    """
    if 'win' in sys.platform:
        with pkg_resources.path(data, 'xpdf-tools-win-4.01.01') as xpdf:
            PDFTOTEXT = xpdf.joinpath('bin64', 'pdftotext.exe')
    else:
        with pkg_resources.path(data, 'xpdf-tools-linux-4.01.01') as xpdf:
            PDFTOTEXT = xpdf.joinpath('bin64', 'pdftotext')

    args = [PDFTOTEXT]
    if options:
        args.extend(options.split())
    args.extend([in_pdf, out_text])
        
    subprocess.run(args)

def clinical_detect_neuroscore_version(wb):
    """
    Detects the clinical neuroscore verion.

    **Parameters**

        wb
            an openpyxl workbook, speed is grealy improved when read_oly=True
            and maybe data_only=True

    **Outputs**

        version
            the neuroscore verion. The possible outputs are keys in 
            CLINICAL_NEUROSCORE_VERSIONS_INDETIFIERS but repeated here:
                2
                3.0
                3.0u1.30
                3.0u10.21.16
                3.0u11.01.16
                3.0u2.3
                3.0ulatest
                Old
            None is returned if the version cannot be identified.
    """
    sheet = wb['Template']
    for version, lookup in CLINICAL_NEUROSCORE_VERSIONS_IDENTIFIERS.items():
        is_version = True
        for rc, value in lookup.items():
            cell_value = sheet.cell(row=rc[0], column=rc[1]).value
            if cell_value:
                cell_value = cell_value.strip()
            if cell_value != value:
                is_version = False
                break
        if is_version:
            return version

    return None

