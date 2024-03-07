"""Script for analysing the output produced by a run."""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.colors import Normalize

from clovars import ROOT_PATH
from clovars.IO import SimulationLoader
from clovars.abstract import CellNode
from clovars.simulation import TreeDrawer2D

SETTINGS = {
    'loader_settings': {
        'simulation_input_folder': ROOT_PATH / 'scripts' / 'batch_run_analysis' / 'batch_TreatmentTime_treatCurveMean',
        'cell_csv_file_name': 'cell_output.csv',
        'colony_csv_file_name': 'colony_output.csv',
        'parameters_file_name': 'params.json',
    },
    'fitness_memory': ['0.1', '0.3', '0.5', '0.7', '0.9'],
    'death_curve_means': ['35.09', '55.09', '75.09'],
}


def main(
        loader_settings: dict,
        fitness_memory: str,
        death_curve_means: str,
) -> None:
    """Main function of this script."""
    # roots = []
    out_folder = loader_settings['simulation_input_folder'] / 'figures'
    out_folder.mkdir(exist_ok=True, parents=True)
    with open(out_folder / 'missing.txt', 'w') as _:
        print('resetting file {missing_file}...')
    _DEFAULT_FILE_NAME_KEYS = ['cell_csv_file_name', 'colony_csv_file_name', 'parameters_file_name']
    initial_file_names = {k: loader_settings[k] for k in _DEFAULT_FILE_NAME_KEYS}
    for hours, death_curve_mean in itertools.product(fitness_memory, death_curve_means):
        # Monkey patch values here
        prefix = f'{hours}tt_{death_curve_mean}mean'
        for file_name in _DEFAULT_FILE_NAME_KEYS:
            loader_settings[file_name] = f'{prefix}_{loader_settings[file_name]}'
        # Load data here
        print(f'Loading from experiment {hours=}, {death_curve_mean=}...')
        loader = SimulationLoader(settings=loader_settings)
        # exp_roots = list(yield_roots(cell_data=loader.cell_data))
        # roots.extend(exp_roots)
        # Export each root to figure here
        for i, root in enumerate(yield_roots(cell_data=loader.cell_data), 1):
            exp_folder = out_folder / prefix
            exp_folder.mkdir(exist_ok=True, parents=True)
            figure_name = f'{prefix}_{i:03d}.png'
            print(f'Creating Fig. {figure_name}...')
            fig = plt.Figure(figsize=(24, 16))
            leaves = [leaf for leaf in root.get_leaves() if not leaf.is_dead()]
            try:
                plot_distance(fig=fig, leaves=leaves)
            except IndexError:
                print(f'Unable to create Fig. {figure_name}, skipping...')
                with open(out_folder / 'missing.txt', 'a') as missing_file:
                    missing_file.write(f'{figure_name}\n')
                continue
            fig.savefig(exp_folder / figure_name)
            plt.close(fig=fig)
        # Restore values here
        for file_name in _DEFAULT_FILE_NAME_KEYS:
            loader_settings[file_name] = initial_file_names[file_name]

    # # Analyse all loaded data here
    # root_idx = 0
    # fig = plt.figure(figsize=(12, 16))
    #
    # def on_key_press(event):
    #     nonlocal roots, root_idx
    #     if event.key == 'right':
    #         root_idx += 1
    #     elif event.key == 'left':
    #         root_idx -= 1
    #     else:
    #         return
    #     root_idx %= len(roots)
    #     ls = [leaf for leaf in roots[root_idx].get_leaves() if not leaf.is_dead()]
    #     fig.clf()
    #     plot_distance(fig=fig, leaves=ls)
    #     fig.canvas.draw_idle()
    #
    # leaves = [leaf for leaf in roots[root_idx].get_leaves() if not leaf.is_dead()]
    # plot_distance(fig=fig, leaves=leaves)
    # fig.canvas.mpl_connect('key_press_event', on_key_press)
    # plt.show()


def yield_roots(cell_data: pd.DataFrame):
    """Returns the root CellNodes of each tree, parsed from the cell_data DataFrame."""
    for root_name, root_data in cell_data.groupby('branch_name', sort=False):
        root_node = get_root_data(
            root_name=root_name,  # noqa
            root_data=root_data,
        )
        yield root_node


def get_root_data(
        root_name: str,
        root_data: pd.DataFrame,
) -> CellNode:
    """
    Builds the entire CellNode tree of a given colony name and returns its root Node.
    Raises ValueError if the given root_name is not present in the DataFrame.
    """
    if root_name not in root_data['name'].values:
        raise ValueError(f'Root name {root_name} not present in the "Name" column!')
    groups = root_data.sort_values(by=['simulation_seconds']).groupby('name')
    root_node = build_tree(
        root_name=root_name,
        groups=groups,
    )
    return root_node


def build_tree(
        root_name: str,
        groups: pd.DataFrameGroupBy,
        node: CellNode | None = None,
) -> CellNode:
    """Recursively builds the CellNode tree from the groups DataFrameGroupBy."""
    try:
        data = groups.get_group(root_name)
    except KeyError:  # Stop condition
        return node
    current_node = node
    for i, data in data.iterrows():
        next_node = CellNode(name=root_name)
        next_node.add_features(**data.to_dict())
        try:
            current_node.add_child(next_node)  # noqa
        except AttributeError:  # current_node is None
            node = next_node  # next_node is actually the root Node
        current_node = next_node
    build_tree(root_name=root_name + '.1', groups=groups, node=current_node)
    build_tree(root_name=root_name + '.2', groups=groups, node=current_node)
    return node


def plot_distance(
        fig: plt.Figure,
        leaves: list[CellNode],
) -> plt.Figure:
    """Plots a distance matrix between Cells."""
    cmap = 'viridis'

    dist_matrix = np.array([
        [leaf1.get_distance(leaf2) for leaf1 in leaves]
        for leaf2 in leaves
    ])
    z = np.array(dist_matrix)
    x, y = np.meshgrid(range(z.shape[0]), range(z.shape[1]))

    spec = fig.add_gridspec(8, 2)

    ax_2d = fig.add_subplot(spec[:3, 0])
    mappable = ax_2d.imshow(z, cmap=cmap)
    plt.colorbar(mappable=mappable, ax=ax_2d)
    # ax_2d.set_title('2D distance matrix between leaves')

    ax_3d = fig.add_subplot(spec[3:, 0], projection='3d')
    _min, _max = z.min(), z.max()  # noqa
    norm = Normalize(_min, _max)
    m = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    m.set_array([])
    facecolors = m.to_rgba(z)
    ax_3d.plot_surface(x, y, -z, rstride=1, cstride=1, facecolors=facecolors)
    # ax_3d.set_title('3D distance between leaves')

    ax_tree = fig.add_subplot(spec[:, 1])
    drawer = TreeDrawer2D()
    drawer.plot_tree(root_node=leaves[0].get_tree_root(), ax=ax_tree)

    return fig


if __name__ == '__main__':
    main(**SETTINGS)
