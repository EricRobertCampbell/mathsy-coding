import numpy as np
import matplotlib.pylab as plt
import pandas as pd
import pymc as pm
from scipy.stats import norm, gaussian_kde
from typing import List

def ranking_to_individual_games(ranking: List[str]) -> pd.DataFrame:
    """ Returns a DataFrame with columns 'Player i', 'Player j', and 'result' """
    data = pd.DataFrame({"Player i": [], "Player j": [], "result": []})
    for player_i in ranking:
        for player_j in ranking[ranking.index(player_i) + 1:]:
            new_row = pd.DataFrame({"Player i": [player_i], "Player j": [player_j], "result": [1]})
            data = pd.concat([data, new_row], ignore_index=True)
    return data

# these are now distributions because we're going to draw from them later to determine the rank order for a given "judgement"
qualities = dict(A=norm(1, 1), B=norm(0, 1), C=norm(-1, 1))
players = list(qualities.keys())
num_rankings = 1000

all_rankings = []
for _ in range(num_rankings):
    results = {player: qualities[player].rvs() for player in qualities}
    ranking = sorted(results, key=results.get, reverse=True)
    all_rankings.append(ranking)

# now generate the individual games
games_data = pd.DataFrame()
for ranking in all_rankings:
    games_data = pd.concat([games_data, ranking_to_individual_games(ranking)], ignore_index=True)

# convert the names of the players to their index (again)
games_data["Player i index"] = games_data.apply(lambda row: players.index(row["Player i"]), axis=1)
games_data["Player j index"] = games_data.apply(lambda row: players.index(row["Player j"]), axis=1)

with pm.Model() as ranking_model:
    quality = pm.Normal("quality", mu=0, sigma=1, shape=3)
    diffs = quality[games_data["Player i index"]] - quality[games_data["Player j index"]]
    prob_win = pm.math.sigmoid(diffs)
    results = pm.Bernoulli("results", prob_win, observed=games_data["result"])
    trace = pm.sample(tune=1000, return_inferencedata=False)

quality_samples = trace.get_values("quality")
samples = [[], [], []]
for index in [0, 1, 2]:
    for draw in quality_samples:
        samples[index].append(draw[index])
kdes = [gaussian_kde(collected_samples) for collected_samples in samples]

# again, graph the results
fig, ax = plt.subplots()
qs = np.linspace(-3, 3, 201)
for index, kde in enumerate(kdes):
    results = kde(qs)
    ax.plot(qs, results, label=players[index])
ax.set_xlabel("Quality")
ax.set_ylabel("Probability Density")
fig.suptitle("Ranking Results")
fig.legend(framealpha=1)
fig.savefig('ranking_from_ranked_data.png', dpi=400)
