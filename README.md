### HPC-Applications
##Ascot5

ASCOT5 is a test-particle orbit-following code for solving minority species’ distribution functions, transport, and losses in tokamaks and stellarators. For questions related to the code or physics, please join our Slack channel.

#Features

ASCOT5 is a test-particle orbit-following code for computing particle orbits in 3D geometry. The output includes particle orbits, phase-space distributions, transport coefficients, and wall loads. ASCOT5 is frequently applied to study fast ions, impurities, neutrals, and runaway electrons in tokamaks and stellarators. Particle orbits are either solved fully, i.e. including the gyro-motion, or in a reduced picture where only the guiding-center trajectory is traced. The code is extensively parallelized and optimized to support simulations with more than ten million markers.

The code is implemented in C and consists of a main program and a library. Simulation input and output is stored in HDF5 format. All pre- and post-processing is done via the Python interface a5py. In addition the repository also contain several codes that supplement the orbit-following simulations.

The repository is maintained by Aalto University and VTT Technical Research Centre of Finland.

#Requirements

Install the requirements or use the module system:

C compiler (Intel)

HDF5

OpenMP

MPI

Python3.10
