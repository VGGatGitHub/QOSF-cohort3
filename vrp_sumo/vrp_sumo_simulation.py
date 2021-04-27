import numpy as np
import os
import vrp_xml_handler
import quantum_optimizer
from itertools import product


# Parameters
project_dir = 'scenario_1'
n = 4
k = 2

# Node definitions
node_dict = {0: '-168940071#1', 1: '4610479#0', 2: '234463931#2', 3: '171826984#2'}

# Estimate cost graph
edge_list = [p for p in product(node_dict.keys(), node_dict.keys()) if p[0] != p[1]]
path_dict = {i: edge_list[i] for i in range(len(edge_list))}
depart_times = range(0, 3600, 300)
departure_schedule = {t: list(path_dict.keys()) for t in reversed(depart_times)}
vrp_xml_handler.build_simulation_route(node_dict, path_dict, departure_schedule, project_dir)
print('Initiating Cost Estimation...')
os.system('sumo -c {0}/osm.sumocfg --tripinfo-output {0}/vrp_cost_sim.xml --no-warnings true'.format(project_dir))
w = vrp_xml_handler.estimate_cost_graph(project_dir + '/vrp_cost_sim.xml', path_dict)

# Build instance
instance = np.zeros((n, n))
for i, j in edge_list:
    instance[i, j] = w[(i, j)]

# Run quantum annealing
quantum_optimizer = quantum_optimizer.QuantumOptimizer(instance, n, k)
Q, g, c, binary_cost = quantum_optimizer.binary_representation()
qp = quantum_optimizer.construct_problem(Q, g, c)
quantum_solution, quantum_cost = quantum_optimizer.solve_problem(qp)

# Extract routes
route_edges = [edge_list[i] for i in range(len(edge_list)) if quantum_solution[i] == 1]
routes = [list(edge) for edge in route_edges if edge[0] == 0]
for route in routes:
    while route[-1] != 0:
        stuck = True
        for edge in route_edges:
            if edge[0] == route[-1]:
                route.append(edge[1])
                stuck = False
                break
        if stuck:
            break

# Run full simulation
routes = [tuple(route) for route in routes]
path_dict = {i: routes[i] for i in range(len(routes))}
depart_times = range(0, 3600, 1200)
schedule = {t: list(path_dict.keys()) for t in reversed(depart_times)}
vrp_xml_handler.build_simulation_route(node_dict, path_dict, schedule)
print('Initiating Full Simulation...')
os.system('sumo -c {0}/osm.sumocfg --tripinfo-output {0}/vrp_full_sim.xml --no-warnings true'.format(project_dir))
print('Optimized Quantum Cost: ', quantum_cost)
