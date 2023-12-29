from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from numpy import pi
from math import asin, sqrt

qreg_q = QuantumRegister(6, 'q')
creg_c = ClassicalRegister(6, 'c')
circuit = QuantumCircuit(qreg_q, creg_c)

circuit.barrier(qreg_q[0])
circuit.barrier(qreg_q[1])
circuit.ry(2 * asin(sqrt(1 / 3)), qreg_q[2])
circuit.ry(2 * asin(sqrt(1 / 5)), qreg_q[5])
circuit.h(qreg_q[0])
circuit.x(qreg_q[2])
circuit.x(qreg_q[5])
circuit.ch(qreg_q[2], qreg_q[1])
circuit.ch(qreg_q[5], qreg_q[4])
circuit.x(qreg_q[2])
circuit.ch(qreg_q[5], qreg_q[3])
circuit.x(qreg_q[5])