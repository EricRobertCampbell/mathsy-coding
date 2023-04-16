import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binom, beta

ps = np.linspace(0, 1, 101)
alpha_param = 3
beta_param = 2
prior = beta(alpha_param, beta_param).pdf(ps)
likelihood = binom(n=10, p=ps).pmf(7)
posterior = prior * likelihood # unnormalized
posterior = posterior / np.sum(posterior) # normalized

max_posterior = np.max(posterior) # probability mass
max_posterior_index = np.argmax(posterior)

fig, ax = plt.subplots()
ax.set_xlabel("$p$")
ax.set_ylabel("Probability density")
ax.plot(ps, prior / np.sum(prior), label="Prior")
ax.plot(ps, posterior, label="Posterior")
ax.axvline(x=2/3, linestyle="--")
ax.annotate(r"$\frac{2}{3}$", xy=(2/3, 0.005), xytext=(0.55, 0.003), arrowprops=dict(arrowstyle='->'))
ax.annotate(f"Posterior max at {ps[max_posterior_index]:.2f}", xytext=(0.2, 0.03), xy=(ps[max_posterior_index], max_posterior), arrowprops=dict(arrowstyle="->"))
fig.legend()
fig.suptitle("Prior and Posterior Distributions of $p$ (Grid)")
fig.savefig("grid.png", dpi=400)
