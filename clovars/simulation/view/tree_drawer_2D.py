from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.animation import ArtistAnimation
from matplotlib.cm import get_cmap
from matplotlib.colors import Normalize

from clovars.utils import QuietPrinterMixin

if TYPE_CHECKING:
    from pathlib import Path
    from clovars.abstract import CellNode


class TreeDrawer2D(QuietPrinterMixin):
    """Class containing functions to draw and display Cell trees in 2D."""
    valid_layouts = [
        'family',
        'time',
        'age',
        'generation',
        'division',
        'death',
        'signal',
    ]

    def __init__(
            self,
            colormap_name: str = 'viridis',
            layout: str = 'family',
            signal_values: pd.Series | None = None,
            time_values: pd.Series | None = None,
            age_values: pd.Series | None = None,
            generation_values: pd.Series | None = None,
            verbose: bool = False,
    ) -> None:
        """Initializes a TreeDrawer2D instance."""
        super().__init__(verbose=verbose)
        self.colormap = get_cmap(colormap_name)
        self.validate_layout(layout=layout)
        self.layout = layout
        self.time_normalizer = self.get_normalizer(values=time_values)
        self.age_normalizer = self.get_normalizer(values=age_values)
        self.generation_normalizer = self.get_normalizer(values=generation_values)
        self.division_normalizer = self.get_normalizer(values=None)
        self.death_normalizer = self.get_normalizer(values=None)
        self.signal_normalizer = self.get_normalizer(values=signal_values)

    def validate_layout(
            self,
            layout: str,
    ) -> None:
        """Raises a ValueError if the given layout isn't a valid option."""
        if layout not in self.valid_layouts:
            raise ValueError(f'Invalid layout: {layout}')

    @staticmethod
    def get_normalizer(values: pd.Series | None = None) -> Normalize:
        """Returns a Normalize instance that normalizes the values in the pandas Series between 0 and 1."""
        if values is None:
            return Normalize(vmin=0, vmax=1)
        if values.empty:
            return Normalize(vmin=0, vmax=1)
        return Normalize(vmin=values.min(), vmax=values.max())

    def display_trees(
            self,
            root_nodes: list[CellNode],
    ) -> None:
        """Displays the trees as a matplotlib 2D plot."""
        for root_node in root_nodes:
            self.plot_tree(root_node=root_node)
            self.quiet_print(f"Displaying colony: {root_node.name}")
            plt.show()

    def render_trees(
            self,
            root_nodes: list[CellNode],
            folder_path: Path,
            file_name: str,
            file_extension: str,
    ) -> None:
        """Renders the trees as a matplotlib 2D plot."""
        for root_node in root_nodes:
            figure = self.plot_tree(root_node=root_node)
            self.quiet_print(f"Rendering image of colony: {root_node.name}")
            fname = str(folder_path / f'{file_name}_{root_node.name}.{file_extension}')
            figure.savefig(fname)
            plt.close(figure)

    def plot_tree(
            self,
            root_node: CellNode,
    ) -> plt.Figure:
        """Plots the tree, given its root node."""
        figure, ax = plt.subplots(figsize=(12, 12))
        self.draw_branches(root_node=root_node, ax=ax)
        self.draw_cells(root_node=root_node, ax=ax)
        self.hide_borders(ax=ax)
        if self.layout == 'family':  # add legend for family layout only
            self.add_legend(ax=ax)
        if self.layout not in ('family', 'time'):  # add colorbar for other layouts only
            self.add_colorbar(figure=figure, ax=ax)
        figure.suptitle(f'Colony {root_node.name}')
        ax.set_xlabel('Simulation time (hours)')
        ax.set_ylabel('')
        plt.tight_layout()
        return figure

    def draw_branches(
            self,
            root_node: CellNode,
            ax: plt.Axes,
    ) -> None:
        """Draws the branches between parent and child nodes in the tree."""
        for node in root_node.traverse():
            parent_x = node.simulation_hours
            parent_y = self.get_height_from_name(name=node.name)
            for child_node in node.children:
                child_x = child_node.simulation_hours
                child_y = self.get_height_from_name(name=child_node.name)
                xs = [parent_x, child_x]
                ys = [parent_y, child_y]
                ax.plot(xs, ys, c='0.7', linewidth=0.5, zorder=1)

    def draw_cells(
            self,
            root_node: CellNode,
            ax: plt.Axes,
    ) -> None:
        """Draws the individual cells in the tree."""
        xs, ys, colors, markers, sizes = [], [], [], [], []
        for node in root_node.traverse():
            xs.append(self.get_node_x(node=node))
            ys.append(self.get_node_y(node=node))
            colors.append(self.get_node_color(node=node))
            markers.append(self.get_node_marker(node=node))
            sizes.append(self.get_node_size(node=node))
        x_array = np.array(xs)
        y_array = np.array(ys)
        color_array = np.array(colors)
        marker_array = np.array(markers)
        size_array = np.array(sizes)
        for marker in np.unique(marker_array):  # each marker must be plotted in a different ax.scatter call!
            indices = np.where(marker_array == marker)
            ax.scatter(
                x_array[indices],
                y_array[indices],
                c=color_array[indices],
                s=size_array[indices],
                marker=marker,
                zorder=2,
            )

    @staticmethod
    def get_node_x(node: CellNode) -> float:
        """Returns the CellNode's X position in the plot."""
        return node.simulation_hours

    def get_node_y(
            self,
            node: CellNode,
    ) -> float:
        """Returns the CellNode's Y position in the plot."""
        return self.get_height_from_name(name=node.name)

    @staticmethod
    def get_height_from_name(name: str) -> float:
        """Returns the height of the CellNode in a 2D tree, given its name."""
        height = 0.0
        current_step = 0.5
        for number in name.split('.')[1:]:
            if number == '1':
                height += current_step
            elif number == '2':
                height -= current_step
            current_step /= 2
        return height

    def get_node_color(
            self,
            node: CellNode,
    ) -> float | str:
        """Returns the CellNode's color in the plot."""
        return {
            'family': self.get_family_color,
            'time': self.get_time_color,
            'age': self.get_age_color,
            'generation': self.get_generation_color,
            'division': self.get_division_color,
            'death': self.get_death_color,
            'signal': self.get_signal_color,
        }[self.layout](node=node)

    @staticmethod
    def get_family_color(node: CellNode) -> str:
        """Returns the CellNode's color in the plot, when plotting the tree with the family layout."""
        if node.is_initial_cell():
            return '#3e5199'
        elif node.is_dead():
            return '#993e50'
        elif node.is_leaf():
            return 'gray'
        elif node.is_parent():
            return '#50993e'
        else:
            return 'gray'

    def get_time_color(
            self,
            node: CellNode
    ) -> str:
        """Returns the CellNode's color in the plot, when plotting the tree with the time layout."""
        return self.colormap(self.time_normalizer(node.simulation_hours))

    def get_age_color(
            self,
            node: CellNode
    ) -> str:
        """Returns the CellNode's color in the plot, when plotting the tree with the age layout."""
        return self.colormap(self.age_normalizer(node.seconds_since_birth / 3600))  # in hours

    def get_generation_color(
            self,
            node: CellNode
    ) -> str:
        """Returns the CellNode's color in the plot, when plotting the tree with the generation layout."""
        return self.colormap(self.generation_normalizer(node.generation))

    def get_division_color(
            self,
            node: CellNode
    ) -> str:
        """Returns the CellNode's color in the plot, when plotting the tree with the division layout."""
        return self.colormap(self.division_normalizer(node.division_threshold))

    def get_death_color(
            self,
            node: CellNode
    ) -> str:
        """Returns the CellNode's color in the plot, when plotting the tree with the death layout."""
        return self.colormap(self.death_normalizer(node.death_threshold))

    def get_signal_color(
            self,
            node: CellNode
    ) -> str:
        """Returns the CellNode's color in the plot, when plotting the tree with the signal layout."""
        return self.colormap(self.signal_normalizer(node.signal_value))

    def get_node_marker(
            self,
            node: CellNode,
    ) -> str:
        """Returns the CellNode's marker in the plot."""
        if self.layout == 'family':
            return self.get_family_marker(node=node)
        else:
            return '.'

    @staticmethod
    def get_family_marker(node: CellNode) -> str:
        """Returns the CellNode's marker in the plot, when plotting the tree with the family layout."""
        if node.is_initial_cell():
            return 'o'
        elif node.is_dead():
            return 'X'
        elif node.is_leaf():
            return '.'
        elif node.is_parent():
            return 'o'
        else:  # regular node
            return '.'

    def get_node_size(
            self,
            node: CellNode,
    ) -> float:
        """Returns the CellNode's size in the plot."""
        if self.layout == 'family':
            return self.get_family_size(node=node)
        else:
            return 15.0

    @staticmethod
    def get_family_size(node: CellNode) -> float:
        """Returns the CellNode's size in the plot, when plotting the tree with the family layout."""
        if node.is_initial_cell():
            return 50.0
        elif node.is_dead():
            return 50.0
        elif node.is_leaf():
            return 15.0
        elif node.is_parent():
            return 50.0
        else:  # regular node
            return 15.0

    @staticmethod
    def hide_borders(ax: plt.Axes) -> None:
        """Hides unnecessary borders from the Axes instance."""
        ax.yaxis.set_visible(False)
        for direction in ['right', 'top', 'left']:
            ax.spines[direction].set_visible(False)

    @staticmethod
    def add_legend(ax: plt.Axes) -> None:
        """Adds a legend to the Figure."""
        handles = [
            plt.Line2D([0], [0], marker='.', color='w', markerfacecolor='gray', markersize=15, label='cell'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#3e5199', markersize=15, label='root cell'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#50993e', markersize=15, label='parent cell'),
            plt.Line2D([0], [0], marker='X', color='w', markerfacecolor='#993e50', markersize=15, label='dead cell'),
        ]
        ax.legend(handles=handles)

    def add_colorbar(
            self,
            figure: plt.Figure,
            ax: plt.Axes,
    ) -> None:
        """Adds a colorbar to the Figure."""
        norm = {
            'age': self.age_normalizer,
            'generation': self.generation_normalizer,
            'division': self.division_normalizer,
            'death': self.death_normalizer,
            'signal': self.signal_normalizer,
        }[self.layout]
        label = {
            'age': 'Cell Age (h)',
            'generation': 'Generation',
            'division': 'Division Threshold',
            'death': 'Death Threshold',
            'signal': 'Signal Value',
        }[self.layout]
        mappable = plt.cm.ScalarMappable(norm=norm, cmap=self.colormap)
        figure.colorbar(mappable=mappable, ax=ax, label=label, orientation='horizontal', fraction=0.05)

    def render_tree_videos(
            self,
            root_nodes: list[CellNode],
            folder_path: Path,
            file_name: str,
            file_extension: str,
    ) -> None:
        """Renders the trees as a matplotlib 2D plot."""
        for root_node in root_nodes:
            animation = self.animate_tree(root_node=root_node)
            fname = str(folder_path / f'{file_name}_{root_node.name}.{file_extension}')
            self.quiet_print(f'Rendering video of colony: {root_node.name}')

            def progress_callback(
                    current_frame: int,
                    total_frames: int,
            ) -> None:
                """Prints the current animation progress to stdout."""
                if total_frames is None:
                    total_frames = root_node.get_farthest_node()[0].simulation_frames
                self.quiet_print(f'Writing frame {current_frame} / {total_frames}')

            animation.save(fname, progress_callback=progress_callback)

    def animate_tree(
            self,
            root_node: CellNode,
    ) -> ArtistAnimation:
        """Animates the tree, given its root node."""
        figure, ax = plt.subplots(figsize=(12, 12))
        self.hide_borders(ax=ax)
        if self.layout == 'family':  # add legend for family layout only
            self.add_legend(ax=ax)
        if self.layout not in ('family', 'time'):  # add colorbar for other layouts only
            self.add_colorbar(figure=figure, ax=ax)
        artists = self.animate_frames(root_node=root_node, ax=ax)
        figure.suptitle(f'Colony {root_node.name}')
        ax.set_xlabel('Simulation time (hours)')
        ax.set_ylabel('')
        return ArtistAnimation(figure, artists=artists, interval=200, blit=True)

    def animate_frames(
            self,
            root_node: CellNode,
            ax: plt.Axes,
    ) -> list[list[plt.Artist]]:
        """Animates the frames (as the Simulation advances) in the tree."""
        artist_dict = defaultdict(list)
        for node in root_node.traverse():
            parent_x = self.get_node_x(node=node)
            parent_y = self.get_node_y(node=node)
            node_artists = ax.scatter(
                parent_x,
                parent_y,
                color=self.get_node_color(node=node),
                s=self.get_node_size(node=node),
                marker=self.get_node_marker(node=node),
                zorder=2,
                animated=True,
            )
            artist_dict[node.simulation_frames].append(node_artists)
            for child_node in node.children:
                child_x = self.get_node_x(node=child_node)
                child_y = self.get_node_y(node=child_node)
                xs = [parent_x, child_x]
                ys = [parent_y, child_y]
                line_artists = ax.plot(xs, ys, color='0.7', linewidth=0.5, zorder=1, animated=True)
                artist_dict[child_node.simulation_frames].extend(line_artists)
        # copies the old frames into the current frame
        for frame_number in list(artist_dict.keys()):
            artist_dict[frame_number+1].extend(artist_dict[frame_number])
        return [artist_list for k, artist_list in sorted(artist_dict.items(), key=lambda tup: tup[0])]
