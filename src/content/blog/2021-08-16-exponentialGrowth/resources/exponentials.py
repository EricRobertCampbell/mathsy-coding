import math
import numpy as np
import matplotlib.pyplot as plt

k_disc = 2
k_cont = math.log(k_disc)

continuous_xs = np.linspace(0, 5, 1000)
continuous_ys = [math.exp(k_cont * x) for x in continuous_xs]

discrete_xs = range(0, 5 + 1)
discrete_ys = [k_disc ** x for x in discrete_xs]

fig, ax = plt.subplots()
plt.title("Discrete and Continuous Exponential Growth")
plt.xlabel("Time (years)")
plt.ylabel("Population")
ax.plot(continuous_xs, continuous_ys, "g-", label="Continuous")
ax.plot(discrete_xs, discrete_ys, "ro", label="Discrete")
ax.legend()
plt.savefig("exponentials")
