import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit

def logistic(x, A, k, x_0, offset) -> float:
    expected = A / (1 + np.exp(-k * (x - x_0))) + offset
    return expected

df = pd.read_csv('./tyrannosaurus_growth_table.csv', dtype={'age': np.double, 'mass': np.double})

paper_values = [5551, 0.57, 16.1, 5]

popt, pcov = curve_fit(logistic, df.age, df.mass, p0=paper_values)
A, k, x_0, offset = popt

# for plotting the fitted curve
ages = np.linspace(0, 30, 101)
masses = logistic(ages, *popt)
paper_masses = logistic(ages, *paper_values)

fig, ax = plt.subplots()
fig.suptitle("Tyrannosaurus Rex Growth Curve")
ax.plot('age', 'mass', 'ko', data=df, label="Data")
ax.plot(ages, masses, 'k-', label="Fitted Curve")
ax.plot(ages, paper_masses, 'r--', label="Paper Curve")
ax.set_xlabel('Age (Years)')
ax.set_ylabel('Mass (kg)')
ax.legend()
fig.savefig("tyrannosaurus_growth_curve_with_paper.jpg")
