# Main Project: An Exploration of the Vehicle Routing Problem

## Table of Contents 

- [Introduction](#Introduction)
- [Project Description](#Project-Description)
- [Technologies](#Technologies)
- [How To Use](#How-To-Use)
- [YouTube Tutorials](#YouTube-Tutorials)
- [References](#References)

## Introduction 

The major challenge of the logistics industry is to come up with a delivery plan for hundreds and thousands of delivery clients with a given number of available vehicles. The optimal delivery plan should minimize cost and maximize efficiency. This mathematical problem is known as the Vehicle Routing Problem (VRP). There are various constraints to consider in this problem such as the number of vehicles, vehicles' capacity, the time window of stores, number of depots, traffic, etc.

## Project Description

In this project, we look at the case of vrp with a single depot and a fixed number of vehicles. Here we try to minimize the total distance covered by the vehicles using D-Wave Systems. We compare various quantum algorithms against each other using different D-Wave solvers. We also compare quantum results against the classical CPLEX results.

The vehicle_routing directory contains the core solvers for solving the Vehicle Routing Problem. API usage instructions may be found in the code docstrings. Example usage is shown in the [***Vehicle Routing.ipynb***](https://github.com/VGGatGitHub/QOSF-cohort3/blob/main/vehicle_routing/Vehicle%20Routing%20Problem.ipynb) notebook.

The sub directory [Performance_Comparision](https://github.com/VGGatGitHub/QOSF-cohort3/tree/main/vehicle_routing/Performance_Comparisons) in the vehicle_routing directory has jupyter notebooks displaying classical cpu runtimes and quantum processing unit (qpu) runtimes for various quantum algorithms.

## Technologies
- Python 3
- Qiskit
- Qiskit-optimization
- D-Wave Leap
- D-Wave Ocean SDK

## How To Use
### On D-Wave Leap
- Login to D-Wave Leap Account
- Point your browser to https://ide.dwavesys.io/#https://github.com/VGGatGitHub/QOSF-cohort3
- Using Leap IDE terminal install qiskit, qiskit-optimization:
  - pip install qiskit
  - pip install qiskit-optimization
  - Navigate to the [***Vehicle Routing.ipynb***](https://github.com/VGGatGitHub/QOSF-cohort3/blob/main/vehicle_routing/Vehicle%20Routing%20Problem.ipynb) notebook in the vehicle_routing directory, and run the first cell. The Leap IDE will direct the user to install jupyter server and other data science tools.
- [***Vehicle Routing.ipynb***](https://github.com/VGGatGitHub/QOSF-cohort3/blob/main/vehicle_routing/Vehicle%20Routing%20Problem.ipynb) notebook in the vehicle_routing directory has examples on how to use the code for solving vehicle routing problem using different solvers and backends.

### On Local System
- It is recommended to use a seperate conda environment for the project, although this is not necessary. Visit the [anaconda installation page](https://docs.anaconda.com/anaconda/install) for more info.
- You need access to a D-Wave leap account. Visit the [leap sign-up page](https://www.dwavesys.com/take-leap) for signing up.
- Install the following python packages
  - pip install qiskit
  - pip install qiskit-optimization
  - pip install dwave-ocean-sdk
- Run dwave setup on your terminal and follow through the steps in the [D-Wave Getting Started Guide](https://docs.ocean.dwavesys.com/en/stable/overview/install.html)
- Clone the repo to your system and run whichever solver you want. [***Vehicle Routing.ipynb***](https://github.com/VGGatGitHub/QOSF-cohort3/blob/main/vehicle_routing/Vehicle%20Routing%20Problem.ipynb) notebook in the vehicle_routing directory has examples on how to use the code for solving vehicle routing problem using different solvers and backends.

## YouTube Tutorials
Description
- playlist link coming soon!

## References
1. Feld, Sebastian, et al. "A hybrid solution method for the capacitated vehicle routing problem using a quantum annealer." Frontiers in ICT 6 (2019): 13.
2. Lucas, Andrew. "Ising formulations of many NP problems." Frontiers in Physics 2 (2014): 5.
3. Borowski, Michał, et al. "New Hybrid Quantum Annealing Algorithms for Solving Vehicle Routing Problem." International Conference on Computational Science. Springer, Cham, 2020.
4. Irie, Hirotaka, et al. "Quantum annealing of vehicle routing problem with time, state and capacity." International Workshop on Quantum Technology and Optimization Problems. Springer, Cham, 2019.
