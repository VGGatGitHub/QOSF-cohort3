import numpy as np

from collections import Counter
from vehicle_routing import VehicleRouter
from qiskit.optimization import QuadraticProgram


class AveragePartitionSolver(VehicleRouter):

    def __init__(self, n_clients=None, n_vehicles=None, cost_matrix=None, constraint_penalty=1e7, limit_radius=2):

        # Call parent initializer
        super().__init__(n_clients, n_vehicles, cost_matrix, constraint_penalty)
        self.limit_radius = limit_radius

    def build_quadratic_program(self):

        # Initialization
        self.qp = QuadraticProgram(name='Vehicle Routing Problem')
        tn = min(self.n, int(np.ceil(self.n / self.m) + self.limit_radius))

        # Designate variable names
        self.variables = np.array([[['x.{}.{}.{}'.format(i, j, k) for k in range(1, tn + 1)]
                                    for j in range(self.n + 1)] for i in range(1, self.m + 1)])

        # Add variables to quadratic program
        for var in self.variables.reshape(-1):
            self.qp.binary_var(name=var)

        # Build objective function
        obj_linear_a = {self.variables[m, n, 0]: self.c[0, n] for m in range(self.m) for n in range(1, self.n + 1)}
        obj_linear_b = {self.variables[m, n, -1]: self.c[n, 0] for m in range(self.m) for n in range(1, self.n + 1)}
        obj_quadratic = {(self.variables[m, i, n], self.variables[m, j, n + 1]): self.c[i, j] for m in range(self.m)
                         for n in range(tn - 1) for i in range(self.n + 1) for j in range(self.n + 1)}

        # Add objective to quadratic program
        self.qp.minimize(linear=dict(Counter(obj_linear_a) + Counter(obj_linear_b)), quadratic=obj_quadratic)

        # Add constraints - single delivery per client
        for k in range(1, self.n + 1):
            constraint_linear = {self.variables[i, k, j]: 1 for i in range(self.m) for j in range(tn)}
            self.qp.linear_constraint(linear=constraint_linear, sense='==', rhs=1, name=f'single_delivery_{k}')

        # Add constraints - vehicle at one place at one time
        for m in range(self.m):
            for n in range(tn):
                constraint_linear = {self.variables[m, k, n]: 1 for k in range(self.n + 1)}
                self.qp.linear_constraint(linear=constraint_linear, sense='==', rhs=1,
                                          name=f'single_location_{m + 1}_{n + 1}')
