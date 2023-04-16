import numpy as np
import matplotlib.pyplot as plt

# data
current_date = 1992 # although the paper was published in 1993, it must have been written in 1992 since that is what Solow uses
sighting_dates = np.array((1915, 1922, 1932, 1948, 1952)) # from LeBoeuf (1986)
normalizing_constant = sighting_dates.min()
normalized_dates = sighting_dates - normalizing_constant # we want to start everything at 0
T = current_date - normalizing_constant

# Visualizing (based on https://matplotlib.org/stable/gallery/lines_bars_and_markers/timeline.html)
dates = np.array([*sighting_dates, current_date])
labels = [f"$t_{index + 1}={normalized_date}$" for index, normalized_date in enumerate(normalized_dates)]
labels.append(f"$T={T}$")
fig, ax = plt.subplots(constrained_layout=True)

ax.set(title="Timeline of Monk Seal Sightings")

# draw the stems and label them - do this first so the lines are under the marker
levels = np.repeat(0.5, dates.shape) + np.array([0.2 * (i % 3 - 1) for i in range(len(labels))])
for date, label, level in zip(dates, labels, levels):
    ax.vlines(date, ymin=0, ymax=level)
    ax.annotate(text=label, xy=(date, level), verticalalignment="bottom", horizontalalignment="center")
ax.plot(dates, # x coords
        np.zeros(dates.shape), # fake y coords - all zeros
        '-o', # solid line, solid circular marker
        color='k', # black
        markerfacecolor='w', # make the markers look hollow
    )

ax.yaxis.set_visible(False)
ax.spines[['left', 'right', 'top']].set_visible(False)

plt.savefig('timeline.png', dpi=800)
