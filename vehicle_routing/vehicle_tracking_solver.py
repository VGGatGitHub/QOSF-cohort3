import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from itertools import product
from collections import Counter
from matplotlib.colors import rgb2hex
from vehicle_routing import VehicleRouter
from qiskit_optimization import QuadraticProgram


class VehicleTrackingSolver(VehicleRouter):

    def __init__(self, n_clients, n_vehicles, cost_matrix, capacities, demands, **params):

        # Store capacity list
        self.capacity = capacities
        self.demand = demands

        # Call parent initializer
        super().__init__(n_clients, n_vehicles, cost_matrix, **params)

    def build_quadratic_program(self):

        # Initialization
        self.qp = QuadraticProgram(name='Vehicle Routing Problem')

        # Designate variable names
        edgelist = [(i, j) for i, j in product(range(self.n + 1), repeat=2) if i != j]
        self.variables = np.array([['x.{}.{}.{}'.format(i, j, k) for i, j in edgelist] for k in range(self.m)])

        # Add variables to quadratic program
        for var in self.variables.reshape(-1):
            self.qp.binary_var(name=var)

        # Add objective to quadratic program
        obj_linear = {f'x.{i}.{j}.{k}': self.c[i, j] for(i, j) in edgelist for k in range(self.m)}
        self.qp.minimize(linear=obj_linear)

        # Add constraints - KCL on nodes
        for j, k in product(range(self.n + 1), range(self.m)):
            constraint_linear_a = {f'x.{i}.{j}.{k}': 1 for i in range(self.n + 1) if i != j}
            constraint_linear_b = {f'x.{j}.{i}.{k}': -1 for i in range(self.n + 1) if i != j}
            constraint_linear = dict(Counter(constraint_linear_a) + Counter(constraint_linear_b))
            self.qp.linear_constraint(linear=constraint_linear, sense='==', rhs=0, name=f'kcl_node_{j}_{k}')

        # Add constraints - single delivery per client
        for j in range(1, self.n + 1):
            constraint_linear = {f'x.{i}.{j}.{k}': 1 for i in range(self.n + 1) for k in range(self.m) if i != j}
            self.qp.linear_constraint(linear=constraint_linear, sense='==', rhs=1, name=f'single_delivery_{j}')

        # Add constraints - all vehicles leave depot
        for k in range(self.m):
            constraint_linear = {f'x.{0}.{j}.{k}': 1 for j in range(1, self.n + 1)}
            self.qp.linear_constraint(linear=constraint_linear, sense='==', rhs=1, name=f'leave_depot_{k}')

        # Add constraints - capacity constraint
        for k in range(self.m):
            constraint_linear = {f'x.{i}.{j}.{k}': self.demand[j - 1] for i, j in edgelist if j != 0}
            self.qp.linear_constraint(linear=constraint_linear, sense='<=', rhs=self.capacity[k], name=f'capacity_{k}')

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
        cmap = plt.cm.get_cmap('Accent')

        # Build graph
        G = nx.MultiDiGraph()
        G.add_nodes_from(range(self.n + 1))

        # Plot nodes
        pos = {i: (xc[i], yc[i]) for i in range(self.n + 1)}
        labels = {i: str(i) for i in range(self.n + 1)}
        nx.draw_networkx_nodes(G, pos=pos, ax=ax, node_color='b', node_size=500, alpha=0.8)
        nx.draw_networkx_labels(G, pos=pos, labels=labels, font_size=16)

        # Plot edges
        var_list = self.variables.reshape(-1)
        sol_list = self.solution.reshape(-1)
        edgelist = [var_list[k] for k in range(len(var_list)) if sol_list[k] == 1]
        edgecolors = [rgb2hex(cmap(int(var.split('.')[3]))) for var in edgelist]
        edgelist = [(int(var.split('.')[1]), int(var.split('.')[2])) for var in edgelist]
        G.add_edges_from(edgelist)
        nx.draw_networkx_edges(G, pos=pos, edgelist=edgelist, width=2, edge_color=edgecolors)

        # Show plot
        plt.grid(True)
        plt.show()
