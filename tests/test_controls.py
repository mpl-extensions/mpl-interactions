from pathlib import Path

import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider

import mpl_interactions.ipyplot as iplt
from mpl_interactions.controller import Controls


def test_eager_register():
    zoop = []

    def cb(**kwargs):
        zoop.append(1)

    ctrls = Controls(beep=(0, 1), boop=(0, 1))
    ctrls.register_callback(cb, None, eager=True)
    assert len(zoop) == 1

    ctrls = Controls(beep=(0, 1), boop=(0, 1))
    ctrls.register_callback(cb, "beep", eager=False)
    assert len(zoop) == 1

    ctrls.controls["beep"].set_val(0.5)
    assert len(zoop) == 2

    ctrls.controls["boop"].set_val(0.5)
    assert len(zoop) == 2


def test_save_animation(tmp_path: Path):
    # just test that no errors are thrown, don't actually check
    # that the saved animation makes any sense. Doing that seems hard :(
    x = np.linspace(0, np.pi, 100)
    tau = widgets.FloatSlider(min=1, max=10, step=1.5)

    def f1(x, amp, tau, beta):
        return amp * np.sin(x * tau) * x * beta

    def f2(x, amp, tau, beta):
        return amp * np.sin(x * beta) * x * tau

    x = np.linspace(0, 2 * np.pi, 200)

    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)
    axfreq = plt.axes([0.25, 0.1, 0.65, 0.03])
    amp_slider = Slider(axfreq, label="amp", valmin=0.05, valmax=10)
    ctrls = Controls(use_ipywidgets=True, tau=tau, beta=(1, 10, 15), amp=amp_slider)
    iplt.plot(x, f1, ax=ax, controls=ctrls)
    iplt.plot(x, f2, ax=ax, controls=ctrls)

    ctrls.save_animation(str(tmp_path / "animation-amp.gif"), fig, "amp", N_frames=10)
    ctrls.save_animation(str(tmp_path / "animation-beta.gif"), fig, "beta")
    ctrls.save_animation(str(tmp_path / "animation-tau.gif"), fig, "tau")


def test_scalar_inside_context():
    x = np.random.randn(20)
    y = 2 * x + np.random.randn(20) / 2

    x2 = np.random.randn(20)
    y2 = -2 * x2 - np.random.randn(20) / 2

    fig, ax = plt.subplots()
    ctrls = iplt.scatter(x, y, s=(10, 1000))
    # this shouldn't fail
    with ctrls:
        _ = iplt.scatter(x2, y2, s=ctrls["s"], ax=ax)
