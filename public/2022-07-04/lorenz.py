from scipy.integrate import solve_ivp
import numpy as np
import matplotlib.pyplot as plt

def func(t, state, sigma, beta, rho):
    x, y, z = state
    dxdt = sigma * (y - x)
    dydt = x * (rho - z)
    dzdt = x * y - beta * z
    return dxdt, dydt, dzdt

y0 = 1, 1, 1
ts = 1, 40
results = solve_ivp(func, ts, y0, args=(10, 8/3, 28), max_step=0.01)

# plot the results as a phase-space diagram
fig = plt.figure(figsize=(20, 20))
ax = fig.gca(projection="3d")
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
ax.plot(results.y[0], results.y[1], results.y[2])

plt.savefig('lorenz.png')

