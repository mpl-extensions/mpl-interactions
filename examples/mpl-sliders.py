# example showing what will happen outside the context of a jupyter notebook
import matplotlib.pyplot as plt
import numpy as np
from mpl_interactions import interactive_plot, interactive_plot_factory

x = np.linspace(0,np.pi,100)
tau = np.linspace(1,10, 100)
beta = np.linspace(.001,1)
def f(x, tau, beta):
    return np.sin(x*tau)*x**beta
fig, ax, sliders = interactive_plot(f, x=x, tau = tau, beta = beta, slider_format_string={'beta': '%1.3e'})
plt.legend()
plt.show()
