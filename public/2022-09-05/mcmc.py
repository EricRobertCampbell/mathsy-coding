import numpy as np
import matplotlib.pyplot as plt
import pymc as pm

from scipy.stats import gaussian_kde, beta

ps = np.linspace(0, 1, 101)
prior = beta(3, 2).pdf(ps)
n = 10
observed_k = 7

with pm.Model() as model:
    p = pm.Beta("p", alpha=3, beta=2)
    k = pm.Binomial("k", p=p, n=n, observed=observed_k)
    samples = pm.sample(tune=2000)


combined_samples = []
for samples_chain in samples.posterior['p']:
    combined_samples.extend(samples_chain)
sample_distribution = gaussian_kde(combined_samples)

posterior = sample_distribution.pdf(ps) #unnormalized
posterior = posterior / np.sum(posterior) #normalized
max_posterior_index = np.argmax(posterior)
max_posterior = np.max(posterior)

fig, ax = plt.subplots()
ax.set_xlabel("$p$")
ax.set_ylabel("Probability density")
ax.plot(ps, prior / np.sum(prior), label="Prior")
ax.plot(ps, posterior, label="Posterior")
ax.axvline(x=2/3, linestyle="--")
ax.annotate(r"$\frac{2}{3}$", xy=(2/3, 0.005), xytext=(0.55, 0.003), arrowprops=dict(arrowstyle='->'))
ax.annotate(f"Posterior max at {ps[max_posterior_index]:.2f}", xytext=(0.2, 0.03), xy=(ps[max_posterior_index], max_posterior), arrowprops=dict(arrowstyle="->"))
fig.legend()
fig.suptitle("Prior and Posterior Distributions of $p$ (MCMC)")
fig.savefig("mcmc.png", dpi=400)
