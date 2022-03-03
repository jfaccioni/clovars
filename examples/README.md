# Examples
This folder contains examples of files used to run CloVarS properly.

### TOML files
These files provide the necessary settings for each of CloVarS' execution modes.

Here's an example of what they look like:
```toml
name = 'John'
number = 20
switch = true

[section]
  key = 'value'
```
Please **do not edit the keys or section names**, only the values on the right-hand side of the `=` sign! CloVarS expects these files to be structured correctly. You can always copy the correct structure from these example files.


### Experimental data
For fitting experimental data into treatments, CloVarS expects a table of values with two columns:
- A column containing the **division times (in hours)** of cells observed in experimental data;
- A column containing the **death times (in hours)** of cells observed in experimental data.

This table should look something like this:

| Division Times | Death Times |
|----------------|-------------|
| 24.3           | 33.5        |
| 12.4           | 56.9        |
| 22.9           | 38.5        |
| 18.8           | 40.0        |
| .....          | .....       |

Both `.csv` and `.xlsx` files are supported. The columns do not need to have the same number of values.

Parameters like file path, column names etc are all read from the corresponding TOML file (see `fit.toml` for an example).