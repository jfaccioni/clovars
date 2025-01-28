from __future__ import annotations

import numpy as np

from clovars.scientific import bounded_brownian_motion


class CellMemory:
    """Class representing a Cell memory, with specific values for mother and sister inheritance."""
    # Actual memory
    _memory_min = -1.0
    _memory_max = 1.0
    # Brownian motion limits
    _fluct_min = 0.0
    _fluct_max = 1.0

    def __init__(
            self,
            mother_memory: float = 0.5,
            sister_memory: float = 0.5,
    ) -> None:
        """Initializes a CellMemory instance."""
        self.mother_memory = mother_memory
        self.sister_memory = sister_memory
        self.validate_memory()

    def validate_memory(self) -> None:
        """Raises a ValueError if any of the memory values are beyond the limits."""
        for memory_value, memory_label in (
                [self.mother_memory, 'Mother'],
                [self.sister_memory, 'Sister'],
        ):
            if not self._memory_min <= memory_value <= self._memory_max:
                raise ValueError(f'Bad memory value for {memory_label} memory: {memory_value}')

    def inherit_from_mother(
            self,
            mother_value: float,
    ) -> float:
        """Inherits the value from the mother, scaled by the mother_memory parameter."""
        scale = np.absolute(self.mother_memory)
        value = bounded_brownian_motion(
            current_value=mother_value,
            scale=scale,
            lower_bound=self._fluct_min,
            upper_bound=self._fluct_max,
        )
        if self.mother_memory < 0:
            return 1 - value
        else:
            return value

    def inherit_from_sister(
            self,
            sister_value: float,
    ) -> float:
        """Inherits the value from the sister, scaled by the sister_memory parameter."""
        scale = np.absolute(self.sister_memory)
        value = bounded_brownian_motion(
            current_value=sister_value,
            scale=scale,
            lower_bound=self._fluct_min,
            upper_bound=self._fluct_max,
        )
        if self.sister_memory < 0:
            return 1 - value
        else:
            return value

# class Inheritable:
#     """Class representing an abstract object that can be inherited from another object."""
#     def __init__(
#             self,
#             value: float = None,
#             memory: float = 0.5,
#             min_value: float = 0.0,
#             max_value: float = 1.0,
#     ) -> None:
#         """Initializes an Inheritable instance."""
#         self.memory = memory
#         self.min = min_value
#         self.max = max_value
#         if value is None:
#             value = self.uniform()
#         self.value = value
#
#     def __str__(self) -> str:
#         """Returns a string representation of the Inheritable."""
#         return f'Inheritable(value={self.value})'
#
#     def inherit(self) -> Inheritable:
#         """Returns another Inheritable object by deriving inherited values."""
#         new_value = self.get_new_value()
#         return self.__class__(value=new_value, memory=self.memory, min_value=self.min, max_value=self.max)
#
#     @property
#     def memory_weight(self):
#         """docs"""
#         if not 0.0 <= self.memory <= 1.0:
#             raise ValueError('Bad memory value!')
#         return self.memory
#
#     @property
#     def stochastic_weight(self):
#         """docs"""
#         return 1 - self.memory
#
#     def get_new_value(self) -> float:
#         """Returns the value of the Inheritable after oscillating it using its memory parameter."""
#         # return self.uniform() * self.stochastic_weight + self.value * self.memory_weight
#         return bounded_brownian_motion(
#             current_value=self.value,
#             scale=self.memory,
#             lower_bound=self.min,
#             upper_bound=self.max,
#         )
#
#     def uniform(self) -> float:
#         """Returns a random value from a uniform distribution, based on the min/max values of the Inheritable."""
#         return np.random.uniform(self.min, self.max)
#
#
# if __name__ == '__main__':
#     dfs = []
#     xs = np.arange(0, 51, 1)
#     for memory_value in (round(x, 2) for x in np.linspace(0.0, 1.0, 9)):
#         for repeat in range(100):
#             ys = []
#             inh = Inheritable(value=0.9, memory=memory_value, min_value=0.0, max_value=1.0)
#             for x in xs:
#                 ys.append(inh.value)
#                 inh = inh.inherit()
#             df = pd.DataFrame({
#                 'memory': memory_value,
#                 'repeat': repeat,
#                 'inheritance_step': xs,
#                 'value': ys,
#             })
#             dfs.append(df)
#     data = pd.concat(dfs, ignore_index=True)
#     autocorrelated_data = data.groupby(['memory', 'repeat'])['value'].apply(pd.Series.autocorr, lag=1).reset_index()
#     # LINEPLOT
#     g = sns.relplot(
#         data=data,
#         kind='line',
#         x='inheritance_step',
#         y='value',
#         col='memory',
#         col_wrap=3,
#         units='repeat',
#         hue='repeat',
#         estimator=None,
#         palette='viridis',
#         legend=None,
#         alpha=0.6,
#     )
#     for ax in g.axes:
#         ax.axhline(0.0, color='black', linestyle='--', alpha=0.5)
#         ax.axhline(1.0, color='black', linestyle='--', alpha=0.5)
#     # VIOLINPLOT
#     fig = plt.figure()
#     sns.violinplot(data=autocorrelated_data, x='memory', y='value')
#     sns.stripplot(data=autocorrelated_data, x='memory', y='value', color='0.3', edgecolor='0.7', linewidth=1)
#
#     plt.show()
