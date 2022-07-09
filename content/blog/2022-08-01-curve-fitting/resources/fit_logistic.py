import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit

def logistic(x, A, k, x_0, offset) -> float:
    expected = A / (1 + np.exp(-k * (x - x_0))) + offset
    # print(f"{ x= }, { expected= }")
    return expected

df = pd.read_csv('./tyrannosaurus_growth_table.csv', dtype={'age': np.double, 'mass': np.double})
print(df)

paper_parameters = [5551, 0.57, 16.1, 5]

popt, pcov = curve_fit(logistic, df.age, df.mass, p0=[5551, 0.57, 16.1, 5], method="trf")
A, k, x_0, offset = popt
print(A, k, x_0, offset)

ages = np.linspace(0, 30, 101)
masses = logistic(ages, *popt)

my_masses = logistic(df.age, *popt)
paper_masses = logistic(df.age, *paper_parameters)
my_error = np.sum((df['mass'] - my_masses) ** 2)
paper_error = np.sum((df['mass'] - paper_masses) ** 2)
print(masses)
print(f"{my_error=}, {paper_error=}")
print(my_error < paper_error)

fig, ax = plt.subplots()
fig.suptitle("Tyrannosaurus Rex Growth Curve")
ax.plot('age', 'mass', 'ko', data=df, label="Data")
ax.plot(ages, logistic(ages, *paper_parameters), label="From Paper")
ax.plot(ages, masses, 'k-', data=df, label="Fitted Curve")
ax.set_xlabel('Age (Years)')
ax.set_ylabel('Mass (kg)')
ax.legend()
fig.savefig("tyrannosaurus_growth_curve.jpg")

