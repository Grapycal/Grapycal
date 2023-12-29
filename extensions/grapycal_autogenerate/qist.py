from qiskit import QuantumCircuit, Aer, execute
from math import asin, sqrt
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from numpy import pi
# Create a quantum circuit
qc = QuantumCircuit(6)

# Apply gates to the circuit based on the provided operations

qc.h(0)
# print(qc)
qc.ry(2 * asin(sqrt(1/3)), 2)
qc.x(2)
qc.ch(2, 1)
qc.x(2)
# qc.h(2)
qc.ry(2 * asin(sqrt(1/5)), 5)
qc.x(5)
qc.ch(5, 4)
qc.ch(5, 3)
qc.x(5)
print(qc)
# Simulate the circuit
backend = Aer.get_backend('statevector_simulator')
job = execute(qc, backend)
result = job.result()
output_state = result.get_statevector(qc)
print(output_state)
