from scipy.integrate import solve_ivp

def func(t, state):
    """ Returns the derivative at the given time and state """
    return state

times = (0, 5)
initial_value = [1]

results = solve_ivp(func, times, initial_value)
print(results)
