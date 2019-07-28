from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='mcw_readers',
    version='0.0.1',
    author='Joe Heffernan',
    author_email='jheffernan@mcw.edu',
    license='MIT',
    description='A package to parse excel and pdf files used by MCW',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/heffjos/mcw_readers',
    packages=find_packages(),
    entry_points={
        'gui_scripts': [
            'mcw_parse_neuros=mcw_readers.cli.mcw_parse_neuros:main',
        ],
    },
    install_requires=[
        'openpyxl',
        'numpy',
        'pandas',
        'importlib_resources',
        'PySimpleGUI',
    ],
    package_data={
        '': ['LICENSE', 'README.md'],
        'mcw_readers': ['data/clinical_versions_labeled.tsv',
                        'data/xpdf-tools-linux-4.01.01/bin64/pdftotext',
                        'data/xpdf-tools-win-4.01.01/bin64/pdftotext.exe'],
    },
    include_package_data=True,
)
