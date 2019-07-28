import sys
import subprocess

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

from . import data

# 12 13 622 632 709 726 739 811
CLINICAL_NEUROSCORE_VERSIONS_IDENTIFIERS = {
    '2': {
        (12, 2):  'COGNITIVE STATUS',
        (13, 2):  None,
        (622, 2): 'Neurologic Impairment',
        (632, 2): 'GSI',
        (709, 2): None,
        (726, 2): None,
        (739, 2): None,
        (811, 2): None},
    '3.0': { 
        (12, 2):  None,
        (13, 2):  'COGNITIVE STATUS',
        (622, 2): 'Somatic Complaints (SOM)',
        (632, 2): 'Drug Problems (DRG)',
        (709, 2): 'PTSD Checklist',
        (726, 2): 'Com',
        (739, 2): 'General Health',
        (811, 2): None},
    '3.0u1.30': {
    # 3.0u2.30
        (12, 2):  'COGNITIVE STATUS',
        (13, 2):  None,
        (622, 2): 'Borderline Featuers (BOR)',
        (632, 2): 'Warmth (WRM)',
        (709, 2): 'SRS Total',
        (726, 2): 'General Health',
        (739, 2): None,
        (811, 2): None},
    '3.0u10.21.16': { 
    # 3.0u11.01.16
        (12, 2):  'COGNITIVE STATUS',
        (13, 2):  None,
        (622, 2): 'Atypical Response (ATR)',
        (632, 2): 'Dysfxn Sexual Behavior (DSB)',
        (709, 2): 'General Health',
        (726, 2): None,
        (739, 2): None,
        (811, 2): None},
    '3.0ulatest': { 
        (12, 2):  None,
        (13, 2):  'COGNITIVE STATUS',
        (622, 2): 'Somatic Problems',
        (632, 2): 'Medication Effects',
        (709, 2): 'Treatment Rejection (RXR)',
        (726, 2): 'MMPI-Rf',
        (739, 2): 'RCd: Demoralization',
        (811, 2): 'General Health'},
    'Old': {
        (12, 2):  'COGNITIVE STATUS',
        (13, 2):  None,
        (622, 2): 'GSI',
        (632, 2): None,
        (709, 2): None,
        (726, 2): None,
        (739, 2): None,
        (811, 2): None},
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
                print('{} {} {}'.format(version, cell_value, value))
                break
        if is_version:
            return version

    return None
    
