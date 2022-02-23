# CloVarS: a clonal variability simulation
This repository contains the source code accompanying the article "CloVarS: a simulation of clonal variability in single cells" (in preparation).

<p align="center" width="100%">
    <img src="docs/_static/clovars_overview.png" alt="CloVarS basic workflow">
</p>

## What is CloVarS
The **Clo**nal **Var**iability **S**imulation (CloVarS) is a cell culture simulation that generates synthetic single-cell lineage data, as normally obtained from time-lapse microscopy experiments.

The example below depicts a single colony, starting from a single cell, which grows over 7 days:

<p align="center" width="100%">
    <img width="80%" src="docs/_static/family_tree_01.gif" alt="Simulation Family Tree">
</p>

## Installation
CloVarS requires **Python version 3.8+** in order to run. You can install CloVarS in your Python environment with the command:
```shell
pip install clovars
```
This adds the `clovars` command to your Python environment, and also installs the necessary [dependencies](#dependencies).

## How to use CloVarS
CloVarS can be executed in the following modes: 
- `run` - run a simulation with the given settings;
- `view` - visualize the results of a previous simulation run (figures, images, videos);
- `analyse` - run analytical tools on the result of a previous simulation run.

You also need to provide the necessary [settings files](settings). These files use the [TOML](https://toml.io/en/) syntax, which makes it easy to open and edit them in any text editor.

[This folder](settings) has examples for the structure of the settings files. **CloVarS will likely run into errors if the setting files have missing / wrong values!**
### Run CloVarS
```shell
clovars run <path-to-run-settings> <path-to-colonies>
```
where: 
- `path-to-run-settings` is the path for a TOML file with the run settings;
- `path-to-colonies` is the path for a TOML file with the colony description.
### View CloVarS
```shell
clovars view <path-to-view-settings>
```
where:
- `path-to-view-settings` is the path for a TOML file with the view settings.
### Analyse CloVarS
```shell
clovars analyse <path-to-analysis-settings>
```
where: 
- `path-to-analysis-settings` is the path for a TOML file with the analysis settings.

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

## Cite us
If you use CloVarS, cite us: *Faccioni, JL; Lenz, G.* (in preparation).
