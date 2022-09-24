import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots()
diffs = np.linspace(-7, 7, 201)
probs = 1 / (1 + np.exp(-diffs))
ax.plot(diffs, probs) # the logistic curve

# This is to illustrate the when the qualities are the same (difference is 0), there is a probability of 0.5 of victory
ax.plot([-7, 0], [0.5, 0.5], 'g--')
ax.plot([0, 0], [0.5, 0], 'g--')

ax.set_yticks(np.linspace(0, 1, 11))
ax.set_xlabel("Difference in Quality $q_i - q_j$")
ax.set_ylabel("Probability of Player $i$'s Victory")
fig.suptitle("Player $i$ Against Player $j$")
fig.savefig('logistic_curve.png', dpi=400)
