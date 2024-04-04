from pathlib import Path

import numpy as np
import pandas as pd

from clovars import ROOT_PATH
from clovars.abstract import CellNode

SETTINGS = {
    'input_folder': ROOT_PATH / 'data' / 'tracking_manual',
    'input_file_name': 'Resultados Tracking ICs.xlsx',
    'sheets_to_analyze': [
        'Camila_01',
        'Camila_02',
        'Camila_03',
        'Camilla_01',
        'Camilla_02',
        'Camilla_03',
        'Letícia_03',
        'Letícia_03',
        'Letícia_03',
    ],
}
MINUTES_IN_FRAME = 30
SECONDS_IN_FRAME = MINUTES_IN_FRAME * 60

SECONDS_IN_HOUR = 60 * 60
SECONDS_IN_DAY = SECONDS_IN_HOUR * 24
CSV_COLUMNS = [
    'id',
    'name',
    'generation',
    'seconds_since_birth',
    'simulation_frames',
    'simulation_seconds',
    'simulation_hours',
    'simulation_days',
    'fate_at_next_frame',
    'branch_name',
    'colony_name',
    'treatment_name',
    'x',
    'y',
    'radius',
    'signal_value',
    'death_threshold',
    'division_threshold',
    'mother_memory',
    'sister_memory',
    'linked_sisters',
]


class ManualTrackingColumns:
    initial_frame = 'Frame inicial'
    final_frame = 'Frame final'
    mother_id = 'ID mãe'
    cell_id = 'ID Célula'
    generation = 'Geração'
    fate_divided = 'Dividiu'
    fate_dead = 'Morreu'
    fate_vanished = 'Sumiu (Fluorescência fraca, saiu do campo, ...)'
    fate_video_end = 'Final do vídeo'


class MetadataKeys:
    researcher_name = 'Nome do Anotador'
    delta_minutes = 'Intervalo de Tempo entre Imagens (min)'



def main(
        input_folder: Path | str,
        input_file_name: str,
        sheets_to_analyze: list[str],
) -> None:
    """Main function of this script."""
    input_folder = Path(input_folder)
    input_path = input_folder / input_file_name
    output_folder = input_folder / 'clovars_format'
    output_folder.mkdir(exist_ok=True, parents=True)
    for i, sheet_name in enumerate(sheets_to_analyze):
        metadata = get_metadata(input_path=input_path, sheet_name=sheet_name)
        tracking_data = get_tracking_data(input_path=input_path, sheet_name=sheet_name)
        tree = build_tree(tracking_data=tracking_data, row_index=i, metadata=metadata)
        output_path = output_folder / f'{sheet_name}_clovars_fmt.csv'
        idx = 0
        with open(output_path, 'w') as clovars_file:
            clovars_file.write(f'index,{",".join(CSV_COLUMNS)}')
            clovars_file.write('\n')
            for node in tree.get_tree_root().traverse():
                clovars_file.write(f'{idx},')
                for feature_name in CSV_COLUMNS:
                    try:
                        feature_value = getattr(node, feature_name)
                    except AttributeError:
                        feature_value = ''
                    if pd.isna(feature_value):
                        feature_value = ''
                    clovars_file.write(f'{feature_value},')
                clovars_file.write('\n')
                idx += 1
        print(f'Finished writing file {output_path}')


def build_tree(
        tracking_data: pd.DataFrame,
        row_index: int,
        metadata: dict,
) -> CellNode:
    """Loads the CellNode from manually tracked data."""
    branch_tip = get_branch_from_row(tracking_data=tracking_data, row_index=row_index, metadata=metadata)
    for child_index in find_children_indices(tracking_data=tracking_data, parent_index=row_index):
        child_branch_tip = build_tree(tracking_data=tracking_data, row_index=child_index, metadata=metadata)
        branch_tip.add_child(child_branch_tip.get_tree_root())
    return branch_tip.get_tree_root()


def get_branch_from_row(
        tracking_data: pd.DataFrame,
        row_index: int,
        metadata: dict,
        current_node: CellNode | None = None,
) -> CellNode | None:
    """Returns a CellNode the given row of the DataFrame (returns None if the row is outside the DataFrame's index)."""
    try:
        cell_row = tracking_data.iloc[row_index]
    except IndexError:
        return None
    start_frame = int(cell_row[ManualTrackingColumns.initial_frame])
    end_frame = int(cell_row[ManualTrackingColumns.final_frame])
    for n_frames_alive in range(end_frame - start_frame + 1):
        current_frame = start_frame + n_frames_alive
        node = get_node_from_row(
            cell_row=cell_row,
            current_frame=current_frame,
            end_frame=end_frame,
            cell_age_in_frames=n_frames_alive,
            metadata=metadata,
        )
        if current_node is not None:
            current_node.add_child(node)  # noqa
        current_node = node
    return current_node


def get_node_from_row(
        cell_row: pd.Series,
        current_frame: int,
        end_frame: int,
        cell_age_in_frames: int,
        metadata: dict,
) -> CellNode:
    """Returns a CellNode for the given row of the tracking data, and for the given frame."""
    researcher_name = metadata[MetadataKeys.researcher_name]
    seconds_in_frame = metadata[MetadataKeys.delta_minutes] * 60
    features = {
        'support': 1.0,
        'dist': 1.0,
        'id': (_id := cell_row[ManualTrackingColumns.cell_id]),
        'name': (_name := f'{researcher_name}-{_id}'),
        'colony_name': researcher_name,
        'branch_name': _name,
        'treatment_name': 'N/A',
        'radius': np.nan,
        'fitness_memory': np.nan,
        'division_threshold': np.nan,
        'death_threshold': np.nan,
        'signal_value': np.nan,
        'x': np.nan,
        'y': np.nan,
        'seconds_since_birth': cell_age_in_frames * seconds_in_frame,
        'simulation_frames': current_frame,
        'simulation_seconds': (_seconds := current_frame * seconds_in_frame),
        'simulation_hours': _seconds / SECONDS_IN_HOUR,
        'simulation_days': _seconds / SECONDS_IN_DAY,
        'generation': cell_row[ManualTrackingColumns.generation],
        'fate_at_next_frame': get_fate_at_next_frame(
            cell_row=cell_row,
            current_frame=current_frame,
            end_frame=end_frame,
        ),
    }
    return CellNode(**features)


def get_fate_at_next_frame(
        cell_row: pd.Series,
        current_frame: int,
        end_frame: int,
) -> str:
    """Returns the cell's fate at the next frame."""
    if current_frame == (end_frame - 1):
        return get_fate_at_final_frame(cell_row=cell_row)
    else:
        return 'migration'


def get_fate_at_final_frame(
        cell_row: pd.Series,
) -> str:
    """Returns the cell's fate at its final frame."""
    if cell_row[ManualTrackingColumns.fate_divided]:
        return 'division'
    elif cell_row[ManualTrackingColumns.fate_dead]:
        return 'death'
    elif cell_row[ManualTrackingColumns.fate_vanished]:
        return 'oob'
    elif cell_row[ManualTrackingColumns.fate_video_end]:
        return 'survival'
    else:
        return 'unknown'


def find_children_indices(
        tracking_data: pd.DataFrame,
        parent_index: int,
) -> list[int]:
    """Returns a list of the indices of the child cells, given the parent's index
    (returns an empty list if no children are found).
    """
    parent_name = tracking_data.loc[parent_index, ManualTrackingColumns.cell_id]
    children_names = tracking_data.loc[tracking_data[ManualTrackingColumns.mother_id] == parent_name]
    if children_names.empty:
        return []
    return children_names.index


def get_metadata(
        input_path: Path,
        sheet_name: str,
) -> dict[str, str | int | float]:
    """Returns the metadata dictionary for the sheet, given its input path and sheet name."""
    dtype_dict = {
        'Nome do Anotador': str,
        'Nome da Primeira Imagem': str,
        'ID Célula Inicial': str,
        'Posição X Célula Inicial': float,
        'Posição Y Célula Inicial': float,
    }
    metatable = pd.read_excel(
        input_path,
        sheet_name=sheet_name,
        dtype=dtype_dict,
        index_col=None,
        decimal=',',
        skiprows=1,
        nrows=2,
    )
    return metatable.iloc[0].to_dict()


def get_tracking_data(
        input_path: Path,
        sheet_name: str,
) -> pd.DataFrame:
    """Returns the tracking DataFrame for the sheet, given its input path and sheet name."""
    dtype_dict = {
        ManualTrackingColumns.generation: float,  # Do not use `int` here, won't work with NaN
        ManualTrackingColumns.mother_id: str,
        ManualTrackingColumns.cell_id: str,
        ManualTrackingColumns.initial_frame: float,
        ManualTrackingColumns.final_frame: float,
        ManualTrackingColumns.fate_dead: bool,
        ManualTrackingColumns.fate_vanished: bool,
        ManualTrackingColumns.fate_video_end: bool,
    }
    tracking_data = pd.read_excel(
        input_path,
        sheet_name=sheet_name,
        dtype=dtype_dict,
        index_col=None,
        skiprows=5,
    )
    return tracking_data.assign(Geração=tracking_data[ManualTrackingColumns.generation].ffill().astype(int))


if __name__ == '__main__':
    main(**SETTINGS)
