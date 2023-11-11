import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import beta

ps = np.linspace(0, 1, 101)

fig, ax = plt.subplots()
ax.set_xlabel("$p$")
ax.set_ylabel("Probability Density")
for alpha_param, beta_param in [(num_successes + 1, num_failures + 1) for num_successes, num_failures in [(2 * k, 1 * k) for k in range(1, 6)]]:
    ax.plot(ps, beta(alpha_param, beta_param).pdf(ps), label=f"Beta({alpha_param}, {beta_param})")
ax.axvline(x=2/3, linestyle="--")
ax.annotate(r"$\frac{2}{3}$", xy=(2/3, 0.5), xytext=(0.5, 0.5), arrowprops=dict(arrowstyle="->"))
fig.legend(loc="center right")
fig.suptitle(f"Beta Distributions With Maximum Values at 2/3")
fig.savefig("differentBetas.png", dpi=400)
