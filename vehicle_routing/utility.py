import numpy as np


def generate_instance(n):

    # Generate VRP instance
    xc = (np.random.rand(n + 1) - 0.5) * 10
    yc = (np.random.rand(n + 1) - 0.5) * 10
    instance = np.zeros((n + 1, n + 1))
    for ii in range(n + 1):
        for jj in range(ii + 1, n + 1):
            instance[ii, jj] = (xc[ii] - xc[jj]) ** 2 + (yc[ii] - yc[jj]) ** 2
            instance[jj, ii] = instance[ii, jj]

    # Return output
    return instance, xc, yc
