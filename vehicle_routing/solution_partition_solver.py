import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from itertools import product
from collections import Counter
from vehicle_routing import VehicleRouter
from qiskit_optimization import QuadraticProgram


class SolutionPartitionSolver(VehicleRouter):

    def __init__(self, n_clients, n_vehicles, cost_matrix, **params):

        # Initialize cluster data
        self.route = None
        self.start_indices = None
        self.end_indices = None

        # Call parent initializer
        super().__init__(n_clients, n_vehicles, cost_matrix, **params)

    def build_quadratic_program(self):

        # Initialization
        self.qp = QuadraticProgram(name='Vehicle Routing Problem')

        # Designate variable names
        self.variables = np.array([[f'x.{i}.{j}' for i in range(1, self.n + 1)] for j in range(1, self.n + 1)])

        # Add variables to quadratic program
        for var in self.variables.reshape(-1):
            self.qp.binary_var(name=var)

        # Build objective function
        edgelist = [(i, j) for i, j in product(range(1, self.n + 1), repeat=2) if i != j]
        obj_linear_a = {f'x.{i}.{1}': self.cost[0, i] for i in range(1, self.n + 1)}
        obj_linear_b = {f'x.{i}.{self.n}': self.cost[i, 0] for i in range(1, self.n + 1)}
        obj_quadratic = {(f'x.{i}.{t}', f'x.{j}.{t + 1}'): self.cost[i, j] for i, j in edgelist
                         for t in range(1, self.n)}

        # Add objective to quadratic program
        self.qp.minimize(linear=dict(Counter(obj_linear_a) + Counter(obj_linear_b)), quadratic=obj_quadratic)

        # Add constraints - single delivery per client
        for i in range(1, self.n + 1):
            constraint_linear = {f'x.{i}.{j}': 1 for j in range(1, self.n + 1)}
            self.qp.linear_constraint(linear=constraint_linear, sense='==', rhs=1, name=f'single_delivery_{i}')

        # Add constraints - vehicle at one place at one time
        for j in range(1, self.n + 1):
            constraint_linear = {f'x.{i}.{j}': 1 for i in range(1, self.n + 1)}
            self.qp.linear_constraint(linear=constraint_linear, sense='==', rhs=1, name=f'single_location_{j}')

    def solve(self, **params):

        # Solve TSP
        super().solve(**params)

        # Evaluate route
        var_list = self.variables.reshape(-1)
        sol_list = self.solution.reshape(-1)
        active_vars = [var_list[k] for k in range(len(var_list)) if sol_list[k] == 1]
        self.route = [int(var.split('.')[1]) for var in active_vars]

        # Evaluate partition costs
        partition_costs = np.zeros(self.n - 1)
        for i in range(self.n - 1):
            partition_costs[i] = self.cost[self.route[i], 0] + self.cost[0, self.route[i + 1]] - \
                                 self.cost[self.route[i], self.route[i + 1]]

        # Evaluate minimum cost partition
        cut_indices = np.argsort(partition_costs)[:(self.m - 1)]
        self.start_indices = np.sort(cut_indices) + 1
        self.start_indices = [0] + list(self.start_indices)
        self.end_indices = np.sort(cut_indices)
        self.end_indices = list(self.end_indices) + [self.n - 1]

    def visualize(self, xc=None, yc=None):

        # Resolve coordinates
        if xc is None:
            xc = (np.random.rand(self.n + 1) - 0.5) * 10
        if yc is None:
            yc = (np.random.rand(self.n + 1) - 0.5) * 10

        # Initialize figure
        plt.figure()
        ax = plt.gca()
        ax.set_title(f'Vehicle Routing Problem - {self.n} Clients & {self.m} Cars')

        # Build graph
        G = nx.MultiDiGraph()
        G.add_nodes_from(range(self.n + 1))

        # Plot nodes
        pos = {i: (xc[i], yc[i]) for i in range(self.n + 1)}
        labels = {i: str(i) for i in range(self.n + 1)}
        nx.draw_networkx_nodes(G, pos=pos, ax=ax, node_color='b', node_size=500, alpha=0.8)
        nx.draw_networkx_labels(G, pos=pos, labels=labels, font_size=16)

        # Loop through cars
        for i in range(self.m):

            # Extract edge list
            route = [self.route[j] for j in range(self.start_indices[i], self.end_indices[i] + 1)]
            edgelist = [(0, route[0])] + [(route[j], route[j + 1]) for j in range(len(route) - 1)] + [(route[-1], 0)]

            # Plot edges
            G.add_edges_from(edgelist)
            nx.draw_networkx_edges(G, pos=pos, edgelist=edgelist, width=2, edge_color='r')

        # Show plot
        plt.grid(True)
        plt.show()
