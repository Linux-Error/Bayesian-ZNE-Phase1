from qiskit import QuantumCircuit,  transpile
from qiskit_aer import AerSimulator, Aer
import pandas as pd

def noisy_cnot_circuit(n):
    qc = QuantumCircuit(n, n)  # Create a circuit with `n` qubits

    # Step 1: Apply a Hadamard to the first qubit to create superposition
    qc.h(0)
    
    # Step 2: Apply controlled rotations to introduce bias
    for i in range(1, n):
        qc.cx(0, i)
        qc.rz((i + 1) * 0.5, i)  # Controlled bias rotations based on qubit index
    
    # Step 3: Apply another layer of entanglement
    for i in range(n - 1):
        qc.cx(i, i + 1)
    
    # Step 4: Add a final biasing layer
    for i in range(n):
        qc.rx(i * 0.3, i)  # Apply small rotations to each qubit
    
    # Step 5: Measurement
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

# Create the circuit
qc = noisy_cnot_circuit(n_qubits)

# Use AerSimulator
simulator = AerSimulator()

# Transpile the circuit for the simulator
transpiled_qc = transpile(qc, simulator)

# Run the simulation
job = simulator.run(transpiled_qc, shots=shots)
result = job.result()

# Get the measurement counts
counts = result.get_counts()

# Calculate the expectation value for the last qubit
expectation_value = calculate_last_qubit_expectation_value(counts, n_qubits)

# Save the result
results = [{"Last Qubit Expectation Value": expectation_value}]



print(f"Expectation Value of the Last Qubit: {expectation_value}")