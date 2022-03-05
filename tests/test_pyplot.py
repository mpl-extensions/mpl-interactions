import matplotlib.pyplot as plt
import numpy as np
from matplotlib import __version__ as mpl_version
from matplotlib.testing.decorators import check_figures_equal
from packaging import version

import mpl_interactions.ipyplot as iplt
from mpl_interactions.pyplot import interactive_plot

from ._util import set_param_values

np.random.seed(1111111121)

mpl_gr_32 = version.parse(mpl_version) >= version.parse("3.3")


def f_hist(loc, scale):
    return np.random.randn(1000) * scale + loc


# # smoke test
# def test_hist_plot(fig_test, fig_ref):
#     fig, ax =
#     test_ax = fig_test.add_subplot()
#     _ = interactive_hist(f_hist, density=True, loc=(5.5, 100), scale=(10, 15), ax=test_ax)


def f1(x, tau, beta):
    return np.sin(x * tau) * x * beta


def f2(x, tau, beta):
    return np.sin(x * beta) * x * tau


def f1(x, tau, beta):
    return np.sin(x * tau) * x * beta


def f2(x, tau, beta):
    return np.sin(x * beta) * x * tau


x = np.linspace(0, np.pi, 100)
tau = (5, 10, 100)
beta = (1, 2)


def test_multiple_functions():
    fig, ax = plt.subplots()
    controls = interactive_plot(x, f1, tau=tau, beta=beta, label="f1")
    interactive_plot(x, f2, controls=controls, label="f2")
    _ = plt.legend()
    return fig


@check_figures_equal(extensions=["png"])
def test_plot(fig_test, fig_ref):
    test_ax = fig_test.add_subplot()

    # TODO: fix the horrible ylim scaling
    # get it outside of the plot command
    ylims = (-10, 10)
    controls = interactive_plot(x, f1, beta=beta, tau=tau, label="f1", ax=test_ax, ylim=ylims)
    interactive_plot(
        x, f2, controls=controls, label="custom label!", linestyle="--", ax=test_ax, ylim=ylims
    )
    set_param_values(controls, {"beta": 5, "tau": 4})
    test_ax.legend()

    ref_ax = fig_ref.add_subplot()
    ref_ax.plot(x, f1(x, **controls.params), label="f1")
    ref_ax.plot(x, f2(x, **controls.params), linestyle="--", label="custom label!")
    ref_ax.legend()
    ref_ax.set_ylim(ylims)
    for fig in controls.control_figures:
        plt.close(fig)


@check_figures_equal(extensions=["png"])
def test_imshow_scalars(fig_test, fig_ref):
    # and by proxy all the scalar handling

    mask_arr = np.random.randn(10, 10) * 10

    def mask(min_distance):
        new_arr = np.copy(mask_arr)
        new_arr[mask_arr < min_distance] = 0
        return new_arr

    test_ax = fig_test.add_subplot()
    ctrls = iplt.imshow(mask, min_distance=(1, 10), alpha=(0, 1), ax=test_ax)
    set_param_values(ctrls, {"min_distance": 5.5, "alpha": 0.75})
    ref_ax = fig_ref.add_subplot()
    print(ctrls.params)
    ref_ax.imshow(mask(ctrls.params["min_distance"]), alpha=ctrls.params["alpha"])
    for fig in ctrls.control_figures:
        plt.close(fig)


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
