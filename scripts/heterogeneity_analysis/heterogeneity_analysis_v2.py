from pathlib import Path

import pandas as pd

from clovars import ROOT_PATH

SETTINGS = {
    'input_folder': ROOT_PATH / 'data' / 'clovars_output' / 'batch_FitnessMemory_treatCurveMean',
    'input_file': '0.1mem_35.09mean_cell_output.csv',
    'fill_value': 0.5,
    'max_depth': 3,  # max_depth = 3 -> vai até 4ª geração
    'eval_hours': [24, 48, 72],
}


def main(
        input_folder: Path | str,
        input_file: Path | str,
        max_depth: int,
        fill_value: float,
        eval_hours: list[int | float],
) -> None:
    input_folder = Path(input_folder)
    input_file = Path(input_file)
    input_path = input_folder / input_file
    df = pd.read_csv(input_path, index_col='index')
    df['branch_info'] = df['name'].str.replace('^1[a-z]+-', '', regex=True)
    out_dfs = []
    for colony_name, colony_df in df.groupby('colony_name'):
        for eval_hour in eval_hours:
            values = colony_df.loc[colony_df['simulation_hours'] == eval_hour, 'branch_info']
            results = dict()
            count_daughters(results=results, values=values, max_depth=max_depth)
            filled_results = fill_zeros(results=results, fill_value=fill_value)
            print(f'--- Colony {colony_name} at {eval_hour}h ---\n{filled_results}\n')
            _out_df = to_frame(results=filled_results, colony_name=colony_name, eval_hour=eval_hour)
            out_dfs.append(_out_df)
    out_df = pd.concat(out_dfs, ignore_index=True)
    output_folder = input_folder / 'het_analysis'
    output_folder.mkdir(exist_ok=True, parents=True)
    output_path = output_folder / f'{input_file.stem}_het_analysis_v2{input_file.suffix}'
    out_df.to_csv(output_path)


def count_daughters(
        results: dict[str, float],
        values: pd.Series,
        max_depth: int = 4,
        curr_level: str | None = None,
        curr_depth: int | None = None,
) -> None:
    """Conta as filhas de cada galho recursivamente."""
    if curr_level is None:
        curr_level = '1'
        curr_depth = 0
    if curr_depth > max_depth:
        return
    results[curr_level] = float(values.str.startswith(curr_level).sum())
    for level_suffix in ['.1', '.2']:
        next_level = curr_level + level_suffix
        next_depth = curr_depth + 1
        count_daughters(
            results=results,
            values=values,
            max_depth=max_depth,
            curr_level=next_level,
            curr_depth=next_depth,
        )


def fill_zeros(
        results: dict[str, float],
        fill_value: float,
) -> dict[str, float]:
    """Retorna um dicionário com os valores zero preenchidos."""
    return {
        k: (v if v != 0.0 else fill_value)
        for k, v in results.items()
    }


def to_frame(
        results: dict[str, float],
        colony_name: str,
        eval_hour: int | float,
) -> pd.DataFrame:
    """Gera um DataFrame dos resultados."""
    branches = list(results.keys())
    gens = [b.count('.') for b in branches]
    counts = list(results.values())
    return pd.DataFrame({
        'colony': colony_name,
        'eval_hour': eval_hour,
        'branch': branches,
        'generation': gens,
        'counts': counts,
    })


if __name__ == '__main__':
    main(**SETTINGS)
