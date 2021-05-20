# Load the packages that are required
import qubo_formulation as qf

from dwave.system import DWaveSampler, EmbeddingComposite
from collections import defaultdict
import dimod

import dwave.inspector

from dimod import BinaryQuadraticModel
from dwave_qbsolv import QBSolv

n = 5
K = n - 1
print(n,K)
initializer = qf.Initializer(n)
xc,yc,instance = initializer.generate_instance()
QUBO_formulator1 = qf.QUBO_formulator(instance, n, K)

Q, g, c, binary_cost = QUBO_formulator1.binary_representation()
Q_dict = defaultdict(float)

for i in range(n*K):
    Q_dict[(i,i)] = Q[i][i]
    for j in range(i+1,n*K):
        Q_dict[(i,j)] = 2*Q[i][j]

Q_dict_lin = defaultdict(float)
for i in range(n*K):
    Q_dict_lin[(i)] = g[i]

offset = c
vartype = dimod.BINARY
BQM = BinaryQuadraticModel(Q_dict_lin,Q_dict, offset, vartype)
sampler = EmbeddingComposite(DWaveSampler())
sampleset = sampler.sample(BQM, num_reads=100, chain_strength=10000)
print(sampleset)

dwave.inspector.show(sampleset)