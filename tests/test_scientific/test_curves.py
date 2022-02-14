import unittest
from unittest import mock
from unittest.mock import MagicMock

import numpy as np
from scipy.stats import exponnorm, gamma, lognorm, norm

from clovars.scientific import AbstractCurve, EMGaussian, Gamma, Gaussian, Lognormal, get_curve


class TestAbstractCurve(unittest.TestCase):
    """Class representing unit-tests for clovars.scientific.curves.Gaussian class."""
    def setUp(self) -> None:
        """Sets up the test case subject (a Gaussian instance)."""
        self.dist = AbstractCurve()

    def tests_call_abstract_curve_calls_cdf_function(self) -> None:
        """Tests whether calling an AbstractCurve is equivalent to calling its cdf function."""
        with mock.patch('clovars.scientific.AbstractCurve.cdf') as mock_cdf:
            self.dist(1)
        mock_cdf.assert_called_once_with(1)

    def test_draw_many_method_calls_curve_rvs_method_with_size_argument(self) -> None:
        """Tests whether the "draw_many" method returns calls the curve's "rvs" method with the given size argument."""
        self.dist.curve.rvs = MagicMock()
        self.dist.draw_many(size=1)
        self.dist.curve.rvs.assert_called_with(size=1)
        self.dist.draw_many(size=10)
        self.dist.curve.rvs.assert_called_with(size=10)

    def test_draw_method_returns_a_single_value_the_curve_rvs_method(self) -> None:
        """Tests whether the "draw" method returns a single value from the curve's "rvs" method."""
        for random_value in [1.0, 99.99, 3.5, 18, -1]:
            self.dist.curve.rvs = MagicMock(return_value=np.array([random_value]))
            actual_value = self.dist.draw()
            with self.subTest(expected=random_value, actual=actual_value):
                self.assertEqual(random_value, actual_value)

    def test_cdf_method_calls_curve_cdf_method_with_the_x_argument(self) -> None:
        """Tests whether the "cdf" method returns calls the curve's "cdf" method with the given x argument."""
        self.dist.curve.cdf = MagicMock()
        self.dist.cdf(x=1)
        self.dist.curve.cdf.assert_called_with(1)
        self.dist.cdf(x=10)
        self.dist.curve.cdf.assert_called_with(10)

    def test_pdf_method_calls_curve_cdf_method_with_the_x_argument(self) -> None:
        """Tests whether the "pdf" method returns calls the curve's "pdf" method with the given x argument."""
        self.dist.curve.pdf = MagicMock()
        self.dist.pdf(x=1)
        self.dist.curve.pdf.assert_called_with(1)
        self.dist.pdf(x=10)
        self.dist.curve.pdf.assert_called_with(10)

    @mock.patch('clovars.scientific.curves.plt.Axes')
    def test_plot_cdf_method_returns_an_axes_instance(
            self,
            mock_axes: MagicMock,
    ) -> None:
        """Tests whether the "plot_cdf" method returns a plt.Axes instance."""
        return_value = self.dist.plot_cdf(ax=mock_axes)
        self.assertIs(return_value, mock_axes)

    @mock.patch('clovars.scientific.curves.plt.Axes')
    def test_plot_cdf_method_calls_the_axes_plot_method(
            self,
            mock_axes: MagicMock,
    ) -> None:
        """Tests whether the "plot_cdf" method calls the "plt.Axes.plot" method."""
        self.dist.plot_cdf(ax=mock_axes)
        mock_axes.plot.assert_called_once()

    @mock.patch('clovars.scientific.curves.plt.Axes')
    @mock.patch('clovars.scientific.curves.plt.gca')
    def test_plot_cdf_method_returns_a_new_axes_instance_when_ax_is_none(
            self,
            mock_get_current_axes: MagicMock,
            mock_axes: MagicMock,
    ) -> None:
        """
        Tests whether the "plot_cdf" method creates and returns a new plt.Axes instance when the "ax" argument is None.
        """
        mock_get_current_axes.return_value = mock_axes
        return_value = self.dist.plot_cdf()
        mock_get_current_axes.assert_called()
        self.assertIs(return_value, mock_axes)

    @mock.patch('clovars.scientific.curves.plt.Axes')
    def test_plot_pdf_method_returns_an_axes_instance(
            self,
            mock_axes: MagicMock,
    ) -> None:
        """Tests whether the "plot_pdf" method returns a plt.Axes instance."""
        return_value = self.dist.plot_pdf(ax=mock_axes)
        self.assertIs(return_value, mock_axes)

    @mock.patch('clovars.scientific.curves.plt.Axes')
    def test_plot_pdf_method_calls_the_axes_plot_method(
            self,
            mock_axes: MagicMock,
    ) -> None:
        """Tests whether the "plot_pdf" method calls the "plt.Axes.plot" method."""
        self.dist.plot_pdf(ax=mock_axes)
        mock_axes.plot.assert_called_once()

    @mock.patch('clovars.scientific.curves.plt.Axes')
    @mock.patch('clovars.scientific.curves.plt.gca')
    def test_plot_pdf_method_returns_a_new_axes_instance_when_ax_is_none(
            self,
            mock_get_current_axes: MagicMock,
            mock_axes: MagicMock,
    ) -> None:
        """
        Tests whether the "plot_pdf" method creates and returns a new plt.Axes instance when the "ax" argument is None.
        """
        mock_get_current_axes.return_value = mock_axes
        return_value = self.dist.plot_pdf()
        mock_get_current_axes.assert_called()
        self.assertIs(return_value, mock_axes)


class TestGaussian(unittest.TestCase):
    """Class representing unit-tests for clovars.scientific.curves.Gaussian class."""

    def setUp(self) -> None:
        """Sets up the test case subject (a Gaussian instance)."""
        self.dist = Gaussian()

    def test_em_gaussian_inherits_from_abstract_curve(self) -> None:
        """Tests whether a Gaussian is an instance of AbstractCurve."""
        self.assertIsInstance(self.dist, AbstractCurve)

    def test_em_gaussian_has_curve_attribute(self) -> None:
        """Tests whether a Gaussian has the "curve" attribute (a scipy.stats.exponnorm instance)."""
        self.assertTrue(hasattr(self.dist, 'curve'))
        self.assertIsInstance(self.dist.curve, type(norm()))


class TestEMGaussian(unittest.TestCase):
    """Class representing unit-tests for clovars.scientific.curves.EMGaussian class."""

    def setUp(self) -> None:
        """Sets up the test case subject (an EMGaussian instance)."""
        self.dist = EMGaussian()

    def test_em_gaussian_inherits_from_abstract_curve(self) -> None:
        """Tests whether an EMGaussian is an instance of AbstractCurve."""
        self.assertIsInstance(self.dist, AbstractCurve)

    def test_em_gaussian_has_curve_attribute(self) -> None:
        """Tests whether an EMGaussian has the "curve" attribute (a scipy.stats.exponnorm instance)."""
        self.assertTrue(hasattr(self.dist, 'curve'))
        self.assertIsInstance(self.dist.curve, type(exponnorm(K=1)))


class TestGamma(unittest.TestCase):
    """Class representing unit-tests for clovars.scientific.curves.Gamma class."""

    def setUp(self) -> None:
        """Sets up the test case subject (a Gamma instance)."""
        self.dist = Gamma()

    def test_gamma_inherits_from_abstract_curve(self) -> None:
        """Tests whether a Gamma is an instance of AbstractCurve."""
        self.assertIsInstance(self.dist, AbstractCurve)

    def test_gamma_has_curve_attribute(self) -> None:
        """Tests whether a Gamma has the "curve" attribute (a scipy.stats.gamma instance)."""
        self.assertTrue(hasattr(self.dist, 'curve'))
        self.assertIsInstance(self.dist.curve, type(gamma(a=1)))


class TestLognormal(unittest.TestCase):
    """Class representing unit-tests for clovars.scientific.curves.Lognormal class."""

    def setUp(self) -> None:
        """Sets up the test case subject (a Lognormal instance)."""
        self.dist = Lognormal()

    def test_lognormal_inherits_from_abstract_curve(self) -> None:
        """Tests whether a Lognormal is an instance of AbstractCurve."""
        self.assertIsInstance(self.dist, AbstractCurve)

    def test_lognormal_has_curve_attribute(self) -> None:
        """Tests whether a Lognormal has the "curve" attribute (a scipy.stats.lognorm instance)."""
        self.assertTrue(hasattr(self.dist, 'curve'))
        self.assertIsInstance(self.dist.curve, type(lognorm(s=1)))


class TestCurvesFunctions(unittest.TestCase):
    """Class representing unit-tests for clovars.scientific.curves free functions."""

    def test_get_curve_function_returns_gaussian_curve_if_name_argument_is_gaussian(self) -> None:
        """
        Tests whether the "get_curve" function returns a Gaussian curve
        when the "name" argument is the string "Gaussian".
        """
        self.assertIsInstance(get_curve(name='Gaussian'), Gaussian)

    def test_get_curve_function_returns_emgaussian_curve_if_name_argument_is_emgaussian(self) -> None:
        """
        Tests whether the "get_curve" function returns an EMGaussian curve
        when the "name" argument is the string "EMGaussian".
        """
        self.assertIsInstance(get_curve(name='EMGaussian'), EMGaussian)

    def test_get_curve_function_returns_gamma_curve_if_name_argument_is_gamma(self) -> None:
        """
        Tests whether the "get_curve" function returns a Gamma curve
        when the "name" argument is the string "Gamma".
        """
        self.assertIsInstance(get_curve(name='Gamma'), Gamma)

    def test_get_curve_function_returns_lognormal_curve_if_name_argument_is_lognormal(self) -> None:
        """
        Tests whether the "get_curve" function returns a Lognormal curve
        when the "name" argument is the string "Lognormal".
        """
        self.assertIsInstance(get_curve(name='Lognormal'), Lognormal)

    def test_get_curve_function_returns_random_curve_if_name_argument_is_random(self) -> None:
        """
        Tests whether the "get_curve" function returns a random curve
        when the "name" argument is the string "Random".
        """
        signals = (Gaussian, EMGaussian, Gamma, Lognormal)
        for _ in range(30):
            self.assertIsInstance(get_curve(name='Random'), signals)

    def test_get_curve_function_returns_gaussian_if_name_argument_is_falsy(self) -> None:
        """
        Tests whether the "get_curve" function returns a Gaussian curve
        when the "name" argument is a falsy value."""
        for falsy_value in ['', None, False, 0]:
            signal = get_curve(name=falsy_value)
            self.assertIsInstance(signal, Gaussian)

    def test_get_curve_function_raises_value_error_if_any_other_name_argument_is_given(self) -> None:
        """
        Tests whether the "get_curve" function raises a ValueError if any other value
        for the "name" argument is used.
        """
        invalid_signal_types = ['Hello', 'sinusoidal', 'ecstatic', '!!!', 1.0, True]
        for invalid_signal_type in invalid_signal_types:
            with self.assertRaises(ValueError):
                get_curve(name=invalid_signal_type)

    def test_get_curve_function_returns_a_curve_with_the_arguments_provided(self) -> None:
        """
        Tests whether the "get_curve" function returns a curve with the arguments passed on to it
        as the correct attributes in the Curve instance.
        """
        for name in ['Gaussian', 'EMGaussian', 'Gamma', 'Lognormal']:
            kwargs = {
                'mean': 0.4,
                'std': 0.1,
                'k': 0.8,
                'a': 0.3,
                's': 0.2,
            }
            with self.subTest(name=name, kwargs=kwargs):
                with mock.patch('clovars.scientific.curves.' + name) as mock_curve:
                    get_curve(name=name, **kwargs)
                if name == 'Gaussian':
                    mock_curve.assert_called_with(loc=kwargs['mean'], scale=kwargs['std'])
                elif name == 'EMGaussian':
                    mock_curve.assert_called_with(loc=kwargs['mean'], scale=kwargs['std'], k=kwargs['k'])
                elif name == 'Gamma':
                    mock_curve.assert_called_with(loc=kwargs['mean'], scale=kwargs['std'], a=kwargs['a'])
                elif name == 'Lognormal':
                    mock_curve.assert_called_with(loc=kwargs['mean'], scale=kwargs['std'], s=kwargs['s'])
                else:
                    self.fail(f'Bad name in test: {name}')


if __name__ == '__main__':
    unittest.main()
