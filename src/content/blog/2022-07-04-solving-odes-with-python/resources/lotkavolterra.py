from scipy.integrate import solve_ivp
import numpy as np
import matplotlib.pyplot as plt

def func(t, state, b, p, r, d):
    x, y = state
    dxdt = x * (b - p * y)
    dydt = y * (r * x - d)
    return dxdt, dydt

times = 0, 15
y_0 = 0.5, 0.5

results = solve_ivp(func, times, y_0, args=(1, 1, 1, 1), max_step=0.01)

fig, ax = plt.subplots()
fig.suptitle("Lotka-Volterra")
ax.set_xlabel('Time')
ax.set_ylabel('Population')
fig.legend()
ax.plot(results.t, results.y[0], label="Prey Population")
ax.plot(results.t, results.y[1], label="Predator Population")
plt.savefig('lotkavolterra.png')

