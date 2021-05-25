import numpy as np


def generate_vrp_instance(n, seed=None):
    # Set seed
    if seed is not None:
        np.random.seed(seed)

    # Generate VRP instance
    xc = (np.random.rand(n + 1) - 0.5) * 10
    yc = (np.random.rand(n + 1) - 0.5) * 10
    instance = np.zeros((n + 1, n + 1))
    for ii in range(n + 1):
        for jj in range(ii + 1, n + 1):
            instance[ii, jj] = np.sqrt((xc[ii] - xc[jj]) ** 2 + (yc[ii] - yc[jj]) ** 2)
            instance[jj, ii] = instance[ii, jj]

    # Return output
    return instance, xc, yc


def generate_cvrp_instance(n, m, seed=None):

    # Set seed
    if seed is not None:
        np.random.seed(seed)

    # Acquire vrp instance
    instance, xc, yc = generate_vrp_instance(n)

    # Generate capacity and demand
    demands = np.random.rand(n) * 100
    capacities = np.random.rand(m)
    capacities = 4 * capacities * sum(demands) / sum(capacities)

    # Floor data
    demands = np.floor(demands)
    capacities = np.floor(capacities)

    # Return output
    return instance, xc, yc, capacities, demands
