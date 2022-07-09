import pandas as pd
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit

def linear_curve(x, m, b) -> float:
    return m * x + b

df = pd.read_csv('./linear_data.csv')

result = curve_fit(linear_curve, df['x'], df['y'])
popt, pcov = result
m, b = popt

fig, ax = plt.subplots()
fig.suptitle('Fitting a Linear Curve')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.plot('x', 'y', 'ko', data=df, label="Raw Data")
ax.plot(df['x'], 2 * df['x'] + 3, 'k-', label="Actual")
ax.plot(df.x, m * df.x + b, 'r--', label="Fitted")
ax.legend()
fig.savefig('fitted_linear_curve.jpg')
