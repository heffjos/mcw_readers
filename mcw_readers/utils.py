import sys
import subprocess

import pandas as pd

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

from . import data

APHASIA_NEUROREADER_MAPPER = {
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

