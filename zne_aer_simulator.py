import csv
import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, thermal_relaxation_error
from qiskit_aer.noise import ReadoutError

# Assuming previous noisy_cnot_circuit, build_scaled_noise_model, and related functions are already defined.

def noisy_cnot_circuit(n):
    qc = QuantumCircuit(n, n)  # Create a circuit with `n` qubits
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

n_qubits = 3
qc = noisy_cnot_circuit(n_qubits)
qc.draw(output='mpl')


def build_scaled_noise_model(qubit_data, noise_factor=1):
    """
    Builds a noise model with parameters scaled by a noise factor.

    Args:
        qubit_data (list of dict): Each dict contains noise parameters for a qubit.
        noise_factor (float): Factor to scale the noise parameters.

    Returns:
        NoiseModel: The constructed and scaled noise model.
    """
    noise_model = NoiseModel()
    
    for qubit in qubit_data:
        qubit_index = qubit['index']
        scaled_T1 = qubit['T1'] / noise_factor
        scaled_T2 = qubit['T2'] / noise_factor

        # 1. Add Readout Error
        readout_confusion_matrix = [
            [1 - qubit['Prob meas0 prep1'], qubit['Prob meas0 prep1']],
            [qubit['Prob meas1 prep0'], 1 - qubit['Prob meas1 prep0']]
        ]
        readout_error = ReadoutError(readout_confusion_matrix)
        noise_model.add_readout_error(readout_error, [qubit_index])

        # 2. Add Thermal Relaxation Errors for single-qubit gates
        for gate, time_ns in qubit['Gate times'].items():
            if time_ns is not None:  # Skip if gate time is not defined
                time_us = time_ns / 1000  # Convert ns to µs
                thermal_error = thermal_relaxation_error(scaled_T1, scaled_T2, time_us)
                if gate in ['id', 'sx', 'x', 'rz']:
                    noise_model.add_quantum_error(thermal_error, gate, [qubit_index])

        # 3. Add Gate Errors for single-qubit gates, scaled
        for gate, error_rate in qubit['Gate errors'].items():
            if isinstance(error_rate, (float, int)) and gate in ['id', 'sx', 'x', 'rz']:
                scaled_error_rate = error_rate * noise_factor
                noise_model.add_quantum_error(depolarizing_error(scaled_error_rate, 1), gate, [qubit_index])

    # 4. Add Two-Qubit Errors for "ecr"
    for qubit in qubit_data:
        if 'ecr' in qubit['Gate errors'] and isinstance(qubit['Gate errors']['ecr'], (float, int)):
            ecr_error_rate = qubit['Gate errors']['ecr'] * noise_factor
            ecr_time_ns = qubit['Gate times'].get('ecr')

            if ecr_time_ns is not None:
                ecr_time_us = ecr_time_ns / 1000  # Convert ns to µs
                thermal_error_qubit_1 = thermal_relaxation_error(
                    qubit_data[0]['T1'] / noise_factor, qubit_data[0]['T2'] / noise_factor, ecr_time_us)
                thermal_error_qubit_2 = thermal_relaxation_error(
                    qubit_data[1]['T1'] / noise_factor, qubit_data[1]['T2'] / noise_factor, ecr_time_us)
                two_qubit_error = thermal_error_qubit_1.expand(thermal_error_qubit_2)
                depolarizing_error_two_qubit = depolarizing_error(ecr_error_rate, 2)
                combined_error = two_qubit_error.compose(depolarizing_error_two_qubit)
                noise_model.add_quantum_error(combined_error, 'ecr', [0, 1])

    return noise_model






qubit_data = [
    {
        'index': 0,
        'T1': 462.022673,  # in µs
        'T2': 414.4535878,  # in µs
        'Frequency': 4.655644224,  # in GHz
        'Anharmonicity': -0.311063246,  # in GHz
        'Readout assignment error': 0.0009,
        'Prob meas0 prep1': 0.0014,
        'Prob meas1 prep0': 0.0004,
        'Readout length': 1244.444444,  # in ns
        'Gate errors': {
            'id': 0.000170616,
            'rz': 0,
            'sx': 0.000170616,
            'x': 0.000170616,
            'ecr': {
                '0_1': 0.003566334005562166,
                '0_14': 0.0072247272320688505
            }
        },
        'Gate times': {
            '0_1': 561.7777777777777,  # in ns
            '0_14': 561.7777777777777  # in ns
        }
    },
    {
        'index': 1,
        'T1': 459.8797394,  # in µs
        'T2': 209.7394157,  # in µs
        'Frequency': 4.53496149,  # in GHz
        'Anharmonicity': -0.313029805,  # in GHz
        'Readout assignment error': 0.0034,
        'Prob meas0 prep1': 0.0044,
        'Prob meas1 prep0': 0.0024,
        'Readout length': 1244.444444,  # in ns
        'Gate errors': {
            'id': 0.0000947129,
            'rz': 0,
            'sx': 0.0000947129,
            'x': 0.0000947129,
            'ecr': {
                '1_2': 0.007504817775057709
            }
        },
        'Gate times': {
            '1_2': 561.7777777777777  # in ns
        }
    },
    {
        'index': 2,
        'T1': 272.6852473,  # in µs
        'T2': 126.5190162,  # in µs
        'Frequency': 4.680129099,  # in GHz
        'Anharmonicity': -0.309256368,  # in GHz
        'Readout assignment error': 0.0029,
        'Prob meas0 prep1': 0.0036,
        'Prob meas1 prep0': 0.0022,
        'Readout length': 1244.444444,  # in ns
        'Gate errors': {
            'id': 0.000122171,
            'rz': 0,
            'sx': 0.000122171,
            'x': 0.000122171,
            'ecr': {
                '2_3': 0.004220124039163747
            }
        },
        'Gate times': {
            '2_3': 561.7777777777777  # in ns
        }
    }
]




noise_model = build_scaled_noise_model(qubit_data)

print(noise_model)

simulator = AerSimulator(method='automatic')

def calculate_last_qubit_expectation_value(counts, n_qubits):
    zero_counts = counts.get('0' * n_qubits, 0)
    one_counts = counts.get('1' * n_qubits, 0)
    total_counts = zero_counts + one_counts
    
    if total_counts == 0:
        return 0
    
    pz_expectation = (zero_counts - one_counts) / total_counts
    return pz_expectation

def amplify_errors(circuit, noise_factor):
    noisy_circuit = circuit.copy()
    for _ in range(noise_factor):
        noisy_circuit = noisy_circuit.compose(circuit, inplace=False)
    return noisy_circuit

def run_zne_experiment_all_values(circuit, noise_factors, simulator, noise_model, num_runs=20000):
    """
    Runs the Zero Noise Extrapolation (ZNE) experiment with the given circuit and noise factors.
    Returns a dictionary with noise factors as keys and lists of all measured expectation values as values.
    """
    all_expectation_values = {factor: [] for factor in noise_factors}
    
    for noise_factor in noise_factors:
        for _ in range(num_runs):  
            amplified_circuit = amplify_errors(circuit, noise_factor)  
            compiled_circuit = transpile(amplified_circuit, simulator)  
            
            result = simulator.run(compiled_circuit, noise_model=noise_model).result()
            counts = result.get_counts()  
            expectation_value = calculate_last_qubit_expectation_value(counts, circuit.num_qubits)
            print(expectation_value)
            all_expectation_values[noise_factor].append(expectation_value)
    
    return all_expectation_values

def export_all_to_csv(all_expectation_values, filename):
    """
    Exports all measured expectation values for each noise factor to a CSV file.
    """
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write header
        header = ['Noise Factor'] + [f'Measurement {i+1}' for i in range(len(next(iter(all_expectation_values.values()))))]
        writer.writerow(header)
        
        # Write rows for each noise factor
        for noise_factor, values in all_expectation_values.items():
            row = [noise_factor] + values
            writer.writerow(row)

# Main code
n_qubits = 3
qc = noisy_cnot_circuit(n_qubits)
simulator = AerSimulator(method='automatic')

# Define noise factors and run ZNE experiment
noise_factors = [1, 3, 5, 7, 9]
all_expectation_values = run_zne_experiment_all_values(qc, noise_factors, simulator, noise_model, num_runs=20000)

# Export all values to CSV
output_filename = 'zne_all_expectation_values_Kyiv_2000.csv'
export_all_to_csv(all_expectation_values, output_filename)
print(f'All measured expectation values exported to {output_filename}')
