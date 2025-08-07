import csv
from qiskit import QuantumCircuit, transpile, ClassicalRegister
from qiskit_ibm_provider import IBMProvider
from qiskit.visualization import plot_histogram
from qiskit.quantum_info import Operator
import numpy as np
import matplotlib.pyplot as plt


provider = IBMProvider()
backend = provider.get_backend('ibm_kyiv')

def create_base_circuit(n):
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
    qc.draw(output='mpl')
    plt.show()
    
    return qc

# Local gate folding
def apply_local_gate_folding(circuit, factor):
    folded_circuit = QuantumCircuit(circuit.num_qubits, circuit.num_clbits)
    for gate in circuit.data:
        if gate[0].name == 'measure':
            folded_circuit.append(gate[0], gate[1], gate[2])
        else:
            for _ in range(factor):
                folded_circuit.append(gate[0], gate[1], gate[2])
                folded_circuit.append(Operator(gate[0]).adjoint(), gate[1], gate[2])
                folded_circuit.append(gate[0], gate[1], gate[2])
    return folded_circuit

# Calculate expectation value
def calculate_last_qubit_expectation_and_std(counts, n_qubits):
    zero_counts = counts.get('0' * n_qubits, 0)
    one_counts = counts.get('1' * n_qubits, 0)
    total_counts = zero_counts + one_counts

    if total_counts == 0:
        return 0, 0

    pz_expectation = (zero_counts - one_counts) / total_counts
    p_zero = zero_counts / total_counts
    p_one = one_counts / total_counts
    variance = (1**2 * p_zero + (-1)**2 * p_one) - pz_expectation**2
    std_dev = np.sqrt(variance)

    return pz_expectation, std_dev

def measure_expectation_values():
    noise_factors = [1, 3, 5, 7, 9, 11, 13, 15, 17]
    n_qubits = 3
    results = []

    base_circuit = create_base_circuit(n_qubits)
    transpiled_circuit = transpile(base_circuit, backend=backend)

    for factor in noise_factors:
        folded_circuit = apply_local_gate_folding(transpiled_circuit, factor)
        transpiled_folded_circuit = transpile(folded_circuit, backend=backend)

        # Execute on backend
        job = backend.run(transpiled_folded_circuit, shots=4000)
        job_result = job.result()
        counts = job_result.get_counts()

        # Calculate expectation value and stdev
        expectation_value, std_dev = calculate_last_qubit_expectation_and_std(counts, n_qubits)
        results.append((factor, expectation_value, std_dev))

    # Save results to CSV
    with open('expectation_values_trial5_9levels.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Noise Factor', 'Expectation Value', 'Standard Deviation'])
        writer.writerows(results)

    return results

if __name__ == "__main__":
    expectation_values = measure_expectation_values()
    print("Expectation values and standard deviations measured and saved to CSV:")
    print(expectation_values)

