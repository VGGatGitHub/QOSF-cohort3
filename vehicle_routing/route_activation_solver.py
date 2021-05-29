import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from itertools import product
from vehicle_routing import VehicleRouter
from qiskit_optimization import QuadraticProgram


class RouteActivationSolver(VehicleRouter):

    def __init__(self, n_clients, n_vehicles, cost_matrix, **params):

        # Call parent initializer
        super().__init__(n_clients, n_vehicles, cost_matrix, **params)

    def build_quadratic_program(self):

        # Initialization
        self.qp = QuadraticProgram(name='Vehicle Routing Problem')

        # Designate variable names
        edgelist = [(i, j) for i, j in product(range(self.n + 1), repeat=2) if i != j]
        self.variables = np.array([f'x.{i}.{j}' for i, j in edgelist])

        # Add variables to quadratic program
        for var in self.variables:
            self.qp.binary_var(name=var)

        # Add objective to quadratic program
        obj_linear = {self.variables[k]: self.cost[i, j] for k, (i, j) in enumerate(edgelist)}
        self.qp.minimize(linear=obj_linear)

        # Add constraints - single delivery per client
        for i in range(1, self.n + 1):
            constraint_linear_a = {f'x.{j}.{i}': 1 for j in range(self.n + 1) if j != i}
            constraint_linear_b = {f'x.{i}.{j}': 1 for j in range(self.n + 1) if j != i}
            self.qp.linear_constraint(linear=constraint_linear_a, sense='==', rhs=1, name=f'single_delivery_a_{i}')
            self.qp.linear_constraint(linear=constraint_linear_b, sense='==', rhs=1, name=f'single_delivery_b_{i}')

        # Add constraints - m vehicles at depot
        constraint_linear_a = {f'x.{0}.{k}': 1 for k in range(1, self.n + 1)}
        constraint_linear_b = {f'x.{k}.{0}': 1 for k in range(1, self.n + 1)}
        self.qp.linear_constraint(linear=constraint_linear_a, sense='==', rhs=self.m, name=f'depot_a')
        self.qp.linear_constraint(linear=constraint_linear_b, sense='==', rhs=self.m, name=f'depot_b')

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

        # Plot edges
        edgelist = [self.variables[i] for i in range(len(self.variables)) if self.solution[i] == 1]
        edgelist = [(int(var.split('.')[1]), int(var.split('.')[2])) for var in edgelist]
        G.add_edges_from(edgelist)
        nx.draw_networkx_edges(G, pos=pos, edgelist=edgelist, width=2, edge_color='r')

        # Show plot
        plt.grid(True)
        plt.show()
