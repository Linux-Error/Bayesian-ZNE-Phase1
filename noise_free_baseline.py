from qiskit import QuantumCircuit,  transpile
from qiskit_aer import AerSimulator, Aer
import pandas as pd

def noisy_cnot_circuit(n):
    qc = QuantumCircuit(n, n) 
    qc.h(0)
    
    for i in range(1, n):
        qc.cx(0, i)
        qc.rz((i + 1) * 0.5, i)
    
    for i in range(n - 1):
        qc.cx(i, i + 1)
    
    for i in range(n):
        qc.rx(i * 0.3, i)
    
    qc.measure(range(n), range(n))
    
    return qc

def calculate_last_qubit_expectation_value(counts, n_qubits):
    zero_counts = counts.get('0' * n_qubits, 0)
    one_counts = counts.get('1' * n_qubits, 0)
    total_counts = zero_counts + one_counts
    
    if total_counts == 0:
        return 0
    
    pz_expectation = (zero_counts - one_counts) / total_counts
    return pz_expectation

# Simulation parameters
n_qubits = 3
shots = 9000

qc = noisy_cnot_circuit(n_qubits)
simulator = AerSimulator()
transpiled_qc = transpile(qc, simulator)

# Run simulation
job = simulator.run(transpiled_qc, shots=shots)
result = job.result()
counts = result.get_counts()

expectation_value = calculate_last_qubit_expectation_value(counts, n_qubits)

results = [{"Last Qubit Expectation Value": expectation_value}]



print(f"Expectation Value of the Last Qubit: {expectation_value}")
