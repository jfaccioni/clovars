# CloVarS: a clonal variability simulation
This repository contains the source code for the article "CloVarS: a simulation of clonal variability in single cells" (in preparation).

<p><img src="docs/_static/clovars_overview.png" alt="CloVarS basic workflow" width=2240></p>

## What is CloVarS
The **Clo**nal **Var**iability **S**imulation (CloVarS) is a cell culture simulation that generates synthetic single-cell lineage data, as normally obtained from time-lapse microscopy experiments.


## Installation
CloVarS requires Python (3.9+) in order to execute.

CloVarS can be installed in your Python environment with the command:
```shell
pip install clovars
```
This command adds the `clovars` command to your Python environment, while also installing the necessary [dependencies](#dependencies).

## How to use CloVarS
CloVarS can be executed in the following modes: 
- `run` - run a simulation with the given settings
- `view` - visualize the results of a previous run (figures, images, videos) 
- `analyse` - run analytical tools on the result of a previous run
### Run CloVarS
To run CloVarS, enter the following command in a terminal:
```shell
clovars run <path-to-settings-file> <path-to-colonies-file>
```
where: 
- `path-to-settings-file` is the path for a TOML file with the run settings;
- `path-to-colonies-file` is the path for a TOML file with the colony description.
### View CloVarS
To view the result of a previous CloVarS run, enter the following command in a terminal:
```shell
clovars view <path-to-settings-file>
```
where `path-to-settings-file` is the path for a TOML file with the view settings.
### Analyse CloVarS
To run analytical scripts on the results of a previous CloVarS run, enter the following command in a terminal:
```shell
clovars analyse <path-to-settings-file>
```
where `path-to-settings-file` is the path for a TOML file with the analysis settings.

## Dependencies
CloVarS depends on the following third-party packages:
- ete3
- matplotlib
- numpy
- pandas
- scipy
- seaborn

## License
CloVarS is distributed under the MIT license. Read the `LICENSE.md` file for details.
