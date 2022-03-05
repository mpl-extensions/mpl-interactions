import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib import __version__ as mpl_version
from packaging import version

import mpl_interactions.ipyplot as iplt
from mpl_interactions.pyplot import interactive_hist, interactive_plot
from mpl_interactions.utils import figure

np.random.seed(1111111121)

mpl_gr_32 = version.parse(mpl_version) >= version.parse("3.3")


def f_hist(loc, scale):
    return np.random.randn(1000) * scale + loc


@pytest.mark.mpl_image_compare(style="default")
def test_hist_plot():
    fig = figure(2)
    _ = interactive_hist(f_hist, density=True, loc=(5.5, 100), scale=(10, 15))
    fig.tight_layout()
    return fig


@pytest.mark.mpl_image_compare(style="default")
def test_hist_controls():
    if not mpl_gr_32:
        pytest.skip("wonky font differences")
    fig, ax = plt.subplots()
    controls = interactive_hist(
        f_hist, density=True, loc=(5.5, 100), scale=(10, 15), slider_formats="{:.1f}"
    )
    return controls.control_figures[0]


def f1(x, tau, beta):
    return np.sin(x * tau) * x * beta


def f2(x, tau, beta):
    return np.sin(x * beta) * x * tau


@pytest.mark.mpl_image_compare(style="default")
def test_mixed_types():
    if not mpl_gr_32:
        pytest.skip("wonky font differences")

    def foo(x, **kwargs):
        return x

    x = np.linspace(0, 1)
    a = np.linspace(0, 10)
    b = (0, 10, 15)
    # set order is determined in part by PYTHONHASHSEED
    # but there doesn't seem to be an easy way to set this for pytest
    # so the unordered set will change its order from test to test :/
    # c = {'this', 'set will be', 'unordered'}
    d = {("this", "set will be", "ordered")}
    e = 0  # this will not get a slider

    # can't test ipywidgets yet
    # no mpl widgets for booleans
    # f = widgets.Checkbox(value=True, description='A checkbox!!')
    return interactive_plot(x, foo, a=a, b=b, d=d, e=e, display=False).control_figures[0]


def f1(x, tau, beta):
    return np.sin(x * tau) * x * beta


def f2(x, tau, beta):
    return np.sin(x * beta) * x * tau


x = np.linspace(0, np.pi, 100)
tau = (5, 10, 100)
beta = (1, 2)


@pytest.mark.mpl_image_compare(style="default")
def test_multiple_functions():
    fig, ax = plt.subplots()
    controls = interactive_plot(x, f1, tau=tau, beta=beta, label="f1")
    interactive_plot(x, f2, controls=controls, label="f2")
    _ = plt.legend()
    return fig


@pytest.mark.mpl_image_compare(style="default")
def test_styling():
    fig, ax = plt.subplots()
    controls = interactive_plot(
        x,
        f1,
        beta=beta,
        tau=tau,
        label="f1",
    )
    iplt.title("the value of tau is: {tau:.2f}", controls=controls["tau"])
    interactive_plot(
        x,
        f2,
        controls=controls,
        label="custom label!",
        linestyle="--",
    )
    plt.legend()
    return fig


def test_imshow_scalars():
    # and by proxy all the scalar handling
    def mask(min_distance):
        return np.random.randn(10, 10)

    fig, ax = plt.subplots()
    iplt.imshow(mask, min_distance=(1, 10), alpha=(0, 1))


def test_title():
    fig, ax = plt.subplots()
    ctrls = iplt.plot(1, 1, E=3e7)
    expected = "E=3.00e+07"
    iplt.title("E={E:.2e}", controls=ctrls)
    assert not isinstance(ctrls.params["E"], np.ndarray)
    assert ax.get_title() == expected
    plt.close()
    fig, ax = plt.subplots()
    ctrls = iplt.plot(1, 1, E=np.array([3e7, 3e9]))
    iplt.title("E={E:.2e}", controls=ctrls)
    assert ax.get_title() == expected
    plt.close()
