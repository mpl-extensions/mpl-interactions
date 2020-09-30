# example showing what will happen outside the context of a jupyter notebook
import matplotlib.pyplot as plt
import numpy as np

from mpl_interactions import interactive_plot

x = np.linspace(0, np.pi, 100)
tau = np.linspace(1, 10, 100)
beta = np.linspace(0.001, 1)


def f(x, tau, beta):
    return np.sin(x * tau) * x ** beta


fig, ax = plt.subplots()
# n.b. while matplotlib sliders use the % style string formatting mpl_interactions
# always uses the the new style {} formatting
controls = interactive_plot(x, f, tau=tau, beta=beta, slider_formats={"beta": "{:.2f}"})
plt.show()
