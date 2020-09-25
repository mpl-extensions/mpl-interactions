import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider

from mpl_interactions import interactive_plot_factory

fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.25)
x = np.linspace(0, 2 * np.pi, 200)


def f(x, freq):
    return np.sin(x * freq)


axfreq = plt.axes([0.25, 0.1, 0.65, 0.03])
slider = Slider(axfreq, label="freq", valmin=0.05, valmax=10)
controls = interactive_plot_factory(ax, f, x=x, freq=slider)
plt.show()
