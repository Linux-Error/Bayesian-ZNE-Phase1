# Bayesian-ZNE-Phase1

This repository contains the complete simulation and execution framework for my research titled:  
"A Combination of Bayesian Inference with Zero-Noise Extrapolation for Quantum Error Mitigation"  
by *Samuel Stryker, Horace Greeley High School*  
Mentor: Dr. Malcolm Carroll, IBM T.J. Watson Research Center


##  Project Overview

In this project, I developed and evaluated a hybrid quantum error mitigation technique combining Bayesian inference with zero-noise extrapolation (ZNE). The approach integrates classically simulated prior distributions with real IBM Quantum hardware measurements to improve the fidelity of extrapolated expectation values.

The main goals were:
- Improve the accuracy and stability of ZNE using Bayesian correction
- Simulate expectation distributions using Aer + custom noise model to accurately simulate the ibm_kyiv backend
- Run hardware trials on ibm_kyiv backend with local gate folding
- Benchmark against noise-free simulations to compute MAE and CI

##  Repository Contents

- `zne_aer_simulator/`: Simulates noisy expectation values using Aer and exports prior distributions
- `ibm_hardware_runs/`: Runs locally folded circuits on IBM Quantum hardware at λ = 1–9
- `noise_free_baseline/`: Simulates the same circuit on a noise-free backend for comparison
- `data/`: Contains CSV results and calibration data

##  Note on Expectation Values

The expectation values were calculated using a simplified metric based on all-0 and all-1 outcomes (e.g., `'000'` and `'111'`), uniformly applied across all runs (noise-free, noisy, Bayesian-corrected). This does **not impact the comparative validity** of results, as all error metrics (MAE, R²) were calculated with respect to the same baseline.

##  Technical Stack

- Python 3.12
- Qiskit 1.2
- Qiskit Aer
- IBM Quantum (ibm_kyiv backend)
- NumPy, Matplotlib

##  Highlights

- **87% reduction in MAE** using Bayesian-corrected ZNE
- **R² improvement** from 0.9617 → 0.9999
- Classical priors generated from 20k-shot Aer simulations
- Hardware runs used 9k shots per λ level (λ = 1, 3, 5, 7, 9)

##  Author

Sam Stryker  
Horace Greeley High School  
Email: samueltownshendstryker@gmail.com
