"""
based on https://matplotlib.org/3.1.0/gallery/user_interfaces/embedding_in_tk_sgskip.html
special thanks to @tacaswell for helping on the matplotlib discourse:
https://discourse.matplotlib.org/t/mpl-iteractions-with-gui-outside-of-jupyter-notebooks/21523/6
"""

import tkinter

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Implement the default Matplotlib key bindings.
from matplotlib.figure import Figure
from matplotlib.widgets import Slider

from mpl_interactions import heatmap_slicer

root = tkinter.Tk()
root.wm_title("Embedding heatmap_slicer Tk gui")

fig = Figure(figsize=(5, 4), dpi=100)


canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.draw()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)


x = np.linspace(0, np.pi, 100)
y = np.linspace(0, 10, 200)
X, Y = np.meshgrid(x, y)
data1 = np.sin(X) + np.exp(np.cos(Y))
data2 = np.cos(X) + np.exp(np.sin(Y))
_, axes = heatmap_slicer(
    x,
    y,
    (data1, data2),
    slices="both",
    heatmap_names=("dataset 1", "dataset 2"),
    labels=("Some wild X variable", "Y axis"),
    interaction_type="move",
    fig=fig,
)


def _quit():
    root.quit()  # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
    # Fatal Python Error: PyEval_RestoreThread: NULL tstate


button = tkinter.Button(master=root, text="Quit", command=_quit)
button.pack(side=tkinter.BOTTOM)

tkinter.mainloop()
