import hybrid
import dwave.inspector

from greedy import SteepestDescentSolver
from dwave.system import LeapHybridSampler
from dwave.system import DWaveSampler, EmbeddingComposite
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit.algorithms import QAOA
from qiskit import Aer


class SolverBackend:

    def __init__(self, vrp):

        # Store relevant data
        self.vrp = vrp
        self.solvers = {'dwave': self.solve_dwave,
                        'leap': self.solve_leap,
                        'hybrid': self.solve_hybrid,
                        'qaoa': self.solve_qaoa}

    def solve(self, solver, **params):

        # Select solver and solve
        solver = self.solvers[solver]
        solver(**params)

    def solve_dwave(self, **params):

        # Resolve parameters
        params['solver'] = 'dwave'
        inspect = params.setdefault('inspect', False)
        post_process = params.setdefault('post_process', False)

        # Solve
        sampler = EmbeddingComposite(DWaveSampler())
        result = sampler.sample(self.vrp.bqm, num_reads=self.vrp.num_reads, chain_strength=self.vrp.chain_strength)

        # Post process
        if not post_process:
            self.vrp.result = result
        else:
            post_processor = SteepestDescentSolver()
            self.vrp.result = post_processor.sample(self.vrp.bqm, num_reads=self.vrp.num_reads, initial_states=result)

        # Extract solution
        result_dict = self.vrp.result.first.sample
        self.vrp.extract_solution(result_dict)

        # Inspection
        if inspect:
            dwave.inspector.show(result)

    def solve_hybrid(self, **params):

        # Resolve parameters
        params['solver'] = 'hybrid'

        # Build sampler workflow
        workflow = hybrid.Loop(
            hybrid.RacingBranches(
                hybrid.InterruptableTabuSampler(),
                hybrid.EnergyImpactDecomposer(size=30, rolling=True, rolling_history=0.75)
                | hybrid.QPUSubproblemAutoEmbeddingSampler()
                | hybrid.SplatComposer()) | hybrid.ArgMin(), convergence=3)

        # Solve
        sampler = hybrid.HybridSampler(workflow)
        self.vrp.result = sampler.sample(self.vrp.bqm, num_reads=self.vrp.num_reads,
                                         chain_strength=self.vrp.chain_strength)

        # Extract solution
        result_dict = self.vrp.result.first.sample
        self.vrp.extract_solution(result_dict)

    def solve_leap(self, **params):

        # Resolve parameters
        params['solver'] = 'leap'

        # Solve
        sampler = LeapHybridSampler()
        self.vrp.result = sampler.sample(self.vrp.bqm)

        # Extract solution
        result_dict = self.vrp.result.first.sample
        self.vrp.extract_solution(result_dict)

    def solve_qaoa(self, **params):

        # Resolve parameters
        params['solver'] = 'qaoa'

        # Build optimizer and solve
        solver = QAOA(quantum_instance=Aer.get_backend('qasm_simulator'))
        optimizer = MinimumEigenOptimizer(min_eigen_solver=solver)
        self.vrp.result = optimizer.solve(self.vrp.qp)

        # Build result dictionary
        result_dict = {self.vrp.result.variable_names[i]: self.vrp.result.x[i]
                       for i in range(len(self.vrp.result.variable_names))}

        # Extract solution
        self.vrp.extract_solution(result_dict)
