from itertools import product
import xml.dom.minidom as minidom
import os


def build_simulation_route(node_dict, path_dict, schedule, project_dir='scenario_1'):

    # Open file
    file = open(project_dir + '/vrp.truck.trips.xml', 'w')

    # Write headers
    file.write('<routes>')

    # Write vehicle type
    file.write('\n\t<vType id="vrp_truck" vClass="truck" color="0,0,1"/>')

    # Write trips
    for n, t in enumerate(sorted(schedule)):
        for path_id in schedule[t]:

            # Get route endpoints
            path = path_dict[path_id]
            i = path[0]
            j = path[-1]

            # Get intermediaries
            int_nodes = list(path[1:-1])
            int_nodes = ' '.join([node_dict[j] for j in int_nodes])
            via_str = '' if int_nodes == '' else ' via="{}"'.format(int_nodes)

            # Generate trip data
            trip = '\n\t<trip id="vrptruck_{}_{}" type="vrp_truck" depart="{:.2f}" departLane="best"' \
                   ' from="{}" to="{}"{}/>'.format(n, path_id, t, node_dict[i], node_dict[j], via_str)

            # Write to file
            file.write(trip)

    # Write footers
    file.write('\n</routes>\n')
    file.close()


def estimate_cost_graph(xml_filename, path_dict):

    # Parse data
    doc = minidom.parse(xml_filename)
    tripinfo = doc.getElementsByTagName('tripinfo')

    # Initialize output
    costs = {}
    counts = {}

    # Get all simulations and extract relevant data
    for data in tripinfo:

        # Ignore irrelevant data
        if data.getAttribute('id')[:len('vrptruck')] != 'vrptruck':
            continue

        # Extract edge
        id_str = data.getAttribute('id').split('_')
        path_id = int(id_str[2])
        edge = tuple(path_dict[path_id])
        costs.setdefault(edge, 0)
        counts.setdefault(edge, 0)

        # Extract data
        costs[edge] += float(data.getAttribute('arrival')) - float(data.getAttribute('depart'))
        counts[edge] += 1

    # Average costs
    costs = {edge: costs[edge] / counts[edge] for edge in costs.keys()}

    # Return costs
    return costs


if __name__ == '__main__':

    # Test code
    project_dir = 'scenario_1'
    node_dict = {0: '-168940071#1', 1: '4610479#0', 2: '234463931#2', 3: '171826984#2'}
    edge_list = [p for p in product(node_dict.keys(), node_dict.keys()) if p[0] != p[1]]
    path_dict = {i: edge_list[i] for i in range(len(edge_list))}
    depart_times = range(0, 3600, 300)
    departure_schedule = {t: list(path_dict.keys()) for t in reversed(depart_times)}
    build_simulation_route(node_dict, path_dict, departure_schedule)
    os.system('sumo -c {0}/osm.sumocfg --tripinfo-output {0}/vrp_cost_sim.xml --no-warnings true'.format(project_dir))
    w = estimate_cost_graph(project_dir + '/vrp_cost_sim.xml', path_dict)
    w = {edge: w[edge] for edge in edge_list}
    print(w)
