import numpy as np

from qiskit import Aer
from qiskit.optimization.algorithms import MinimumEigenOptimizer
from qiskit.optimization.converters import InequalityToEquality, IntegerToBinary, LinearEqualityToPenalty
from dwave.plugins.qiskit import DWaveMinimumEigensolver


class VehicleRouter:

    def __init__(self, n_clients=None, n_vehicles=None, cost_matrix=None, constraint_penalty=1e7):

        # Store inputs
        self.n = n_clients
        self.m = n_vehicles
        self.c = np.array(cost_matrix)
        self.penalty = constraint_penalty

        # Initialization
        self.qp = None
        self.variables = None
        self.result = None
        self.solution = None

    def build_quadratic_program(self):

        # Dummy. Override in child class.
        pass

    def build_qubo(self):

        # Create converters
        converter_a = InequalityToEquality()
        converter_b = IntegerToBinary()
        converter_c = LinearEqualityToPenalty(penalty=self.penalty)

        # Convert to QUBO
        self.qp = converter_a.convert(self.qp)
        self.qp = converter_b.convert(self.qp)
        self.qp = converter_c.convert(self.qp)

    def solve(self):

        # Build QUBO
        self.build_quadratic_program()
        self.build_qubo()

        # Build optimizer and solve
        solver = DWaveMinimumEigensolver()      # QAOA(quantum_instance=Aer.get_backend('qasm_simulator'))
        optimizer = MinimumEigenOptimizer(min_eigen_solver=solver)
        self.result = optimizer.solve(self.qp)

        # Extract solution
        result_dict = {self.result.variable_names[i]: self.result.x[i] for i in range(len(self.result.variable_names))}
        var_list = self.variables.reshape(-1)
        self.solution = np.zeros(var_list.shape)
        for i in range(len(result_dict)):
            self.solution[i] = result_dict[var_list[i]]

        # Reshape result
        self.solution = self.solution.reshape(self.variables.shape)
