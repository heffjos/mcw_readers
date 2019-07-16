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
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'gui_scripts': [
            'mcw_parse_clinical_files=mcw_readers.cli.mcw_parse_clinical_files:main',
        ],
    },
)
