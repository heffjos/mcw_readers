import sys
import subprocess

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

from . import data

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
            PDFTOTEXT = xpdf.joinpath('bin64', 'pdftotext')
    else:
        with pkg_resources.path(data, 'xpdf-tools-linux-4.01.01') as xpdf:
            PDFTOTEXT = xpdf.joinpath('bin64', 'pdftotext')

    args = [PDFTOTEXT]
    if options:
        args.extend(options.split())
    args.extend([in_pdf, out_text])
        
    subprocess.run(args)
