from scipy.integrate import solve_ivp
import numpy as np
import matplotlib.pyplot as plt

def func(t, state):
    """ Returns the derivative at the given time and state """
    return state

times = (0, 5)
initial_value = [1]

results = solve_ivp(func, times, initial_value)

# Now let's plot the results against the actual solution
fig, ax = plt.subplots()
fig.suptitle(f"Solution to df/dt = f(t), f(0) = 1")
ax.set_xlabel('t')
ax.set_ylabel('f(t)')
ax.plot(results.t, results.y[0], label="Solved Numerically") # numerically
ts = np.linspace(*times, 100)
ax.plot(ts, np.exp(ts), label="Exact Solution") # exact
fig.legend()

plt.savefig('1dsystem.png')
