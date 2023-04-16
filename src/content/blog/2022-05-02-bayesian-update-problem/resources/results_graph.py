import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt


fig, axes = plt.subplots(1, 3, sharey=True)

for ax in axes:
    ax.set_xlabel("Coin")
    ax.set_ylabel("Probability")
    ax.set_ylim([0, 1])


categories = ["P(H)=1/2", "P(H)=1"]

ax1, ax2, ax3 = axes
ax1.set_title("Initial Belief (No Data)")
ax2.set_title("One Head")
ax3.set_title("Two Heads")

ax1.bar(categories, [2 / 3, 1 / 3])
ax2.bar(categories, [1 / 2, 1 / 2])
ax3.bar(categories, [1 / 3, 2 / 3])

fig.savefig("results_graph.png")
