import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pymc as pm
from scipy.stats import bernoulli, gaussian_kde

# player name : quality
qualities = dict(A=1, B=0, C=-1)
players = list(qualities.keys())
num_games = 100

data = pd.DataFrame({"Player i":[], "Player j": [], "result": []})
for player_i in players:
    for player_j in players[players.index(player_i) + 1:]:
        prob_victory = 1 / (1 + np.exp(-(qualities[player_i] - qualities[player_j])))
        new_results = pd.DataFrame({"Player i": [player_i] * num_games, "Player j": [player_j] * num_games, "result": bernoulli.rvs(prob_victory, size=num_games)})
        data = pd.concat([data, new_results], ignore_index=True)

# convert the names of the players to their index - this is for the PyMC model we're about to use
data["Player i index"] = data.apply(lambda row: players.index(row["Player i"]), axis=1)
data["Player j index"] = data.apply(lambda row: players.index(row["Player j"]), axis=1)

# Now the model implementation
with pm.Model() as rank_model:
    quality = pm.Normal("quality", mu=0, sigma=1, shape=3)
    diffs = quality[data["Player i index"]] - quality[data["Player j index"]]
    prob_win = pm.math.sigmoid(diffs)
    results = pm.Bernoulli("results", prob_win, observed=data["result"])
    trace = pm.sample(tune=1000, return_inferencedata=False)

#Now let's plot these to see if we get the expected results:

quality_samples = trace.get_values("quality")
quality_samples.shape
samples = [[], [], []] # player 1, player 2, player 3
for index in [0, 1, 2]:
    for draw in quality_samples:
        samples[index].append(draw[index])
kdes = [gaussian_kde(collected_samples) for collected_samples in samples]

fig, ax = plt.subplots()
qs = np.linspace(-3, 3, 201)
for index, kde in enumerate(kdes):
    results = kde(qs)
    ax.plot(qs, results, label=f"{players[index]} - Quality {qualities[players[index]]}")
for player_quality in qualities.values():
    ax.axvline(player_quality, color="black", linestyle='--')
ax.set_xlabel("Quality")
ax.set_ylabel("Probability Density")
fig.suptitle("Ranking Results")
fig.legend(framealpha=1)
fig.savefig('initial_ranking.png', dpi=400)
