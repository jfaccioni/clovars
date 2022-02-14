from setuptools import find_packages, setup

setup(
    name='clovars',
    version='0.1.0',
    packages=find_packages(),
    package_requires=[
        'ete3',
        'matplotlib',
        'numpy',
        'pandas',
        'openpyxl',
        'jsonpickle',
        'PyQt5',
    ]
)
