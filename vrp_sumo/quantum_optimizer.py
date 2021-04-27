import numpy as np
from dwave.plugins.qiskit import DWaveMinimumEigensolver
from qiskit.aqua import aqua_globals
from qiskit.optimization import QuadraticProgram
from qiskit.optimization.algorithms import MinimumEigenOptimizer


class QuantumOptimizer:

    def __init__(self, instance, n, k):
        self.instance = instance
        self.n = n
        self.k = k

    def binary_representation(self, x_sol=0):

        instance = self.instance
        n = self.n
        k = self.k

        A = np.max(instance) * 100
        instance_vec = instance.reshape(n ** 2)
        w_list = [instance_vec[x] for x in range(n ** 2) if instance_vec[x] > 0]
        w = np.zeros(n * (n - 1))
        for ii in range(len(w_list)):
            w[ii] = w_list[ii]

        Id_n = np.eye(n)
        Im_n_1 = np.ones((n - 1, n - 1))
        Iv_n_1 = np.ones(n)
        Iv_n_1[0] = 0
        Iv_n = np.ones(n - 1)
        neg_Iv_n_1 = np.ones(n) - Iv_n_1
        v = np.zeros((n, n * (n - 1)))

        for ii in range(n):
            count = ii - 1
            for jj in range(n * (n - 1)):
                if jj // (n - 1) == ii:
                    count = ii
                if jj // (n - 1) != ii and jj % (n - 1) == count:
                    v[ii][jj] = 1

        vn = np.sum(v[1:], axis=0)
        Q = A * (np.kron(Id_n, Im_n_1) + np.dot(v.T, v))
        g = w - 2 * A * (np.kron(Iv_n_1, Iv_n) + vn.T) - 2 * A * k * (np.kron(neg_Iv_n_1, Iv_n) + v[0].T)
        c = 2 * A * (n - 1) + 2 * A * (k ** 2)

        try:
            max(x_sol)
            fun = lambda x: np.dot(np.around(x), np.dot(Q, np.around(x))) + np.dot(g, np.around(x)) + c
            cost = fun(x_sol)
        except:
            cost = 0

        return Q, g, c, cost

    def construct_problem(self, Q, g, c) -> QuadraticProgram:
        qp = QuadraticProgram()
        for i in range(self.n * (self.n - 1)):
            qp.binary_var(str(i))
        qp.objective.quadratic = Q
        qp.objective.linear = g
        qp.objective.constant = c
        return qp

    def solve_problem(self, qp):
        aqua_globals.random_seed = 10598
        dwave_solver = DWaveMinimumEigensolver()
        optimizer = MinimumEigenOptimizer(min_eigen_solver=dwave_solver)
        result = optimizer.solve(qp)
        _, _, _, level = self.binary_representation(x_sol=result.x)
        return result.x, level
