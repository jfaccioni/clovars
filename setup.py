from setuptools import find_packages, setup

setup(
    name='clovars',
    version='0.1.0',
    entry_points={
        'console_scripts': [
            'clovars = clovars.main:main'
        ],
    },
    packages=find_packages(),
    install_requires=[
        'ete3',
        'matplotlib',
        'numpy',
        'pandas',
        'toml',
        'scipy',
        'seaborn',
        # 'openpyxl',
        # 'jsonpickle',
        # 'PyQt5',
    ]
)
