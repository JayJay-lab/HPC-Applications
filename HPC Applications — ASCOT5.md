# HPC Applications — ASCOT5

## Overview

**ASCOT5** is a high-performance scientific simulation code used in **fusion plasma physics and engineering**. It is an orbit-following code that simulates the motion and behaviour of particles in magnetic-confinement fusion devices such as **tokamaks** and **stellarators**.

ASCOT5 can be used to study:

- Particle transport
- Particle confinement and losses
- Fast ions
- Impurities
- Neutral particles
- Runaway electrons
- Particle distributions
- Wall interactions and loads

In simple terms:

> **ASCOT5 is a virtual laboratory for studying particle behaviour inside a fusion reactor.**


---

# 1. Real-World Purpose

Fusion reactors contain extremely hot plasma that must be controlled and confined using magnetic fields.

Particles inside the plasma do not always remain perfectly confined. Some particles can:

- Remain confined within the plasma
- Move through the plasma
- Lose energy
- Interact with other particles
- Escape magnetic confinement
- Hit reactor components

ASCOT5 allows researchers to simulate these processes computationally.

A simplified workflow is:

```text
Fusion Reactor
      |
      v
Magnetic Field + Plasma + Geometry
      |
      v
    ASCOT5
      |
      v
Particle Orbit Simulation
      |
      +------------------+
      |                  |
      v                  v
 Particle Transport   Particle Losses
      |                  |
      +---------+--------+
                |
                v
       Wall Loads / Distributions
                |
                v
        Scientific Analysis
                |
                v
      Improved Reactor Design
```

This allows researchers to investigate questions such as:

- Will energetic particles remain confined?
- Where will particles be lost?
- Which reactor components receive the largest particle loads?
- How does changing the magnetic configuration affect particle behaviour?
- How do energetic particles and impurities behave?

ASCOT5 is therefore a **scientific simulation tool**, not a fusion reactor itself.

---

# 2. Tokamaks and Stellarators


<img width="1569" height="930" alt="image" src="https://github.com/user-attachments/assets/d9e227fd-d640-4014-8b99-045c7d4fd6b6" />


## Tokamak

A tokamak is a magnetic-confinement fusion device with a toroidal, approximately doughnut-shaped geometry.

Magnetic fields are used to keep the extremely hot plasma away from material surfaces while fusion reactions occur.

ASCOT5 can simulate particle behaviour inside tokamak configurations.

<img width="730" height="447" alt="image" src="https://github.com/user-attachments/assets/8c419bcf-aecd-4349-b951-3b3c8b06c9ad" />



## Stellarator

A stellarator is another type of magnetic-confinement fusion device.

It uses externally generated three-dimensional magnetic fields to confine plasma.

The complex three-dimensional magnetic geometry makes computational particle-orbit modelling particularly important.

ASCOT5 can simulate particle orbits in both tokamak and stellarator configurations.

---

# 3. What Does ASCOT5 Actually Calculate?

ASCOT5 performs numerical calculations of particle motion.

A simplified simulation process is:

```text
Particle State
      |
      v
Evaluate Magnetic/Electric Fields
      |
      v
Calculate Forces / Particle Dynamics
      |
      v
Advance Particle in Time
      |
      v
Update Position and Energy
      |
      v
Check Interactions
      |
      +----> Particle Lost?
      |
      +----> Wall Hit?
      |
      +----> Continue?
      |
      v
Repeat
```

The exact physics depends on the simulation model and configuration.

However, computationally the program repeatedly performs numerical calculations for large numbers of simulated particles.

This creates a workload that can benefit significantly from high-performance computing.

---

# 4. What Is a Marker?

A **marker** is a computational representation used to model particles or particle populations in the simulation.

A marker should not necessarily be interpreted as one literal physical particle.

Conceptually:

```text
Real Plasma
     |
     v
Huge Number of Physical Particles
     |
     v
Numerical Model
     |
     v
Computational Markers
```

The simulation follows these markers and uses their behaviour to estimate physical quantities.

A simulation may therefore involve a very large number of markers:

```text
Marker 1
Marker 2
Marker 3
Marker 4
   .
   .
   .
Marker N
```

This is one of the reasons ASCOT5 is suitable for HPC.

---

# 5. Why ASCOT5 Requires HPC

Consider a simulation containing millions of markers.

Each marker may require repeated calculations involving:

- Position
- Velocity or momentum
- Time
- Electromagnetic fields
- Particle interactions
- Energy evolution
- Boundary conditions

A simplified representation is:

```text
             Millions of Markers
                     |
        +------------+------------+
        |            |            |
        v            v            v
    Process 1    Process 2    Process 3
        |            |            |
        v            v            v
   Marker Set    Marker Set    Marker Set
        |            |            |
        +------------+------------+
                     |
                     v
             Simulation Results
```

Instead of processing everything sequentially on one CPU core, HPC allows the workload to be distributed across multiple computational resources.

---

# 6. ASCOT5 and Parallel Computing

ASCOT5 is designed with several levels of parallelism.

The major technologies relevant to HPC research include:

- **MPI**
- **OpenMP**
- **SIMD / Vectorization**

A simplified architecture is:

```text
              ASCOT5
                 |
       +---------+---------+
       |         |         |
       v         v         v
      MPI      OpenMP     SIMD
       |         |         |
       v         v         v
 Distributed  Shared     Vector
  Processes   Threads   Operations
       |         |         |
       +---------+---------+
                 |
                 v
             CPU Hardware
```

---

# 7. MPI

**MPI (Message Passing Interface)** provides distributed-memory parallelism.

MPI allows multiple processes to work together and communicate with each other.

For example:

```text
                HPC Cluster
                     |
        +------------+------------+
        |                         |
        v                         v
    Compute Node 1           Compute Node 2
        |                         |
   +----+----+               +----+----+
   |    |    |               |    |    |
 MPI  MPI  MPI              MPI  MPI  MPI
```

MPI makes it possible to distribute computational work across multiple processes and potentially multiple HPC nodes.

For this project, MPI is particularly important when investigating how ASCOT5 scales beyond a single machine.

---

# 8. OpenMP

**OpenMP** provides shared-memory parallelism.

For example, a compute node may contain several CPU cores:

```text
Compute Node
     |
     v
+---------------------------+
| CPU                       |
|                           |
| Core 1                    |
| Core 2                    |
| Core 3                    |
| Core 4                    |
| Core 5                    |
| Core 6                    |
| Core 7                    |
| Core 8                    |
+---------------------------+
```

OpenMP allows a process to use multiple CPU threads across these cores.

A simplified view is:

```text
MPI
 |
 +--> Distribute work between processes/nodes
 |
OpenMP
 |
 +--> Parallelize work inside a node
```

---

# 9. SIMD and Vectorization

**SIMD (Single Instruction, Multiple Data)** allows a CPU instruction to operate on multiple data elements simultaneously.

Without vectorization:

```text
A -> Calculation
B -> Calculation
C -> Calculation
D -> Calculation
```

With SIMD:

```text
A B C D
| | | |
+-+-+-+
   |
   v
One Vector Operation
```

This can increase computational throughput for numerical workloads that are suitable for vectorization.

Modern CPUs can therefore potentially perform several numerical operations within a single instruction.

---

# 10. CPU vs Memory Requirements

ASCOT5 should not simply be described as a "CPU-only" application.

Its resource requirements depend on the simulation configuration.

### CPU

The particle-following workload involves many numerical calculations, making CPU performance important.

CPU performance can be affected by:

- Number of cores
- CPU frequency
- Vectorization
- MPI process count
- OpenMP thread count
- Compiler optimizations

### Memory

Memory is also important because simulations may need to store:

```text
RAM
 |
 +-- Magnetic-field data
 +-- Electric-field data
 +-- Plasma data
 +-- Reactor geometry
 +-- Marker state
 +-- Diagnostics
 +-- Simulation results
```

Large or complex simulations can therefore require significant memory.

A useful way to think about it is:

> **CPU resources determine how much computation can be performed concurrently, while memory resources determine how much simulation data can be stored and accessed efficiently.**

---

# 11. ASCOT5 Architecture

A simplified software architecture is:

```text
                    USER
                     |
                     v
                Python / a5py
                     |
          +----------+----------+
          |                     |
          v                     v
     Input Setup           Data Analysis
          |                     |
          +----------+----------+
                     |
                     v
                  ASCOT5
               C Simulation Core
                     |
          +----------+----------+
          |          |          |
          v          v          v
         MPI       OpenMP      SIMD
          |          |          |
          +----------+----------+
                     |
                     v
                HPC Resources
                     |
                     v
                   HDF5
                     |
                     v
            Results / Diagnostics
```

---

# 12. C and Python

ASCOT5 uses a compiled computational core, while Python is used through **a5py** as an interface for interacting with the simulation and analysing data.

Conceptually:

```text
Python / a5py
      |
      | Prepare inputs
      v
ASCOT5 C Core
      |
      | Heavy numerical computation
      v
Simulation Results
      |
      v
HDF5
      |
      v
Python / a5py
      |
      v
Analysis + Visualisation
```

This distinction is important.

Python provides convenience and flexibility, while the computationally intensive simulation is handled by compiled code.

---

# 13. HDF5

ASCOT5 uses **HDF5** for storing simulation data.

HDF5 is a format designed for large and structured scientific datasets.

A simplified representation of an ASCOT5 HDF5 file might look like:

```text
ascot.h5
 |
 +-- bfield
 |     +-- Magnetic Field Data
 |
 +-- efield
 |     +-- Electric Field Data
 |
 +-- plasma
 |     +-- Plasma Data
 |
 +-- wall
 |     +-- Reactor Geometry
 |
 +-- run_XXXXXXXX
       +-- Simulation Results
```

This allows simulation inputs and results to be organised within a structured scientific data format.

---

# 14. ASCOT5 Ecosystem

ASCOT5 is part of a wider collection of tools used in fusion research.

Examples include:

### BBNBI

Used for modelling neutral beam injection-related quantities and can provide particle sources for ASCOT5 simulations.

### AFSI

Used to calculate fusion-product sources from plasma and fast-ion distributions.

### BioSaw

Calculates magnetic fields from coil geometry and can provide three-dimensional magnetic fields for ASCOT5.

### BMC

A backward Monte Carlo tool related to ASCOT5 and useful for applications such as diagnostic signals and wall-load estimation.

These tools should be viewed as **supporting components around the ASCOT5 ecosystem**, rather than being the ASCOT5 simulation core itself.

---

# 15. HPC Software Stack

For this research project, it is important to distinguish ASCOT5 from the infrastructure used to execute and monitor it.

```text
+----------------------------------+
|         Scientific Application   |
|             ASCOT5               |
+----------------------------------+
                |
+----------------------------------+
|          Parallel Computing      |
|       MPI + OpenMP + SIMD        |
+----------------------------------+
                |
+----------------------------------+
|       Scientific Data Layer      |
|              HDF5                |
+----------------------------------+
                |
+----------------------------------+
|          Compiler / Toolchain    |
|        GCC / Intel / Other       |
+----------------------------------+
                |
+----------------------------------+
|         HPC Cluster Layer        |
|              Slurm               |
+----------------------------------+
                |
+----------------------------------+
|          Monitoring Layer        |
|       Prometheus + Grafana       |
+----------------------------------+
                |
+----------------------------------+
|             Hardware             |
|        CPU + RAM + Network       |
+----------------------------------+
```

### Important distinction

| Technology | Purpose |
|---|---|
| **ASCOT5** | Scientific simulation |
| **HDF5** | Scientific data storage |
| **MPI** | Distributed-memory parallelism |
| **OpenMP** | Shared-memory parallelism |
| **SIMD** | CPU vectorization |
| **GCC / Intel / other compilers** | Build and optimization toolchain |
| **Slurm** | HPC job scheduling |
| **Prometheus** | Metrics collection |
| **Grafana** | Monitoring and visualization |

---

# 16. Installation Environment

The ASCOT5 Python interface requires a modern Python environment.

The current project specifies:

```text
Python >= 3.10
```

The software environment can include components such as:

```text
Python
NumPy
SciPy
HDF5
C Compiler
MPI
OpenMP
a5py
ASCOT5
```

A simplified software stack is:

```text
Operating System
       |
       v
C Compiler
       |
       +--> OpenMP
       |
       +--> MPI
       |
       v
HDF5
       |
       v
Python >= 3.10
       |
       v
a5py
       |
       v
ASCOT5
```

For HPC research, it is important to distinguish between:

1. A local installation used for development and analysis.
2. An MPI-enabled production installation used for distributed HPC simulations.

A working Python/Jupyter environment does **not automatically mean that an MPI-enabled production workload is being executed**.

---

# 17. What Should Be Benchmarked?

The main goal of this project is to investigate ASCOT5 as an HPC workload.

Useful measurements include:

- Execution time
- CPU utilization
- Memory utilization
- Memory bandwidth
- MPI process count
- OpenMP thread count
- Number of markers
- I/O performance
- Parallel speedup
- Parallel efficiency

---

# 18. Execution Time

The most basic performance metric is execution time.

For example:

```text
1 Core   -> 100 minutes
2 Cores  -> 55 minutes
4 Cores  -> 30 minutes
8 Cores  -> 17 minutes
```

The goal is to determine how execution time changes as more computational resources are used.

---

# 19. Speedup

Speedup measures how much faster the simulation becomes when additional resources are used.

The basic formula is:

\[
S(N) = \frac{T_1}{T_N}
\]

Where:

- \(T_1\) = execution time using the baseline configuration
- \(T_N\) = execution time using \(N\) resources
- \(S(N)\) = speedup

For example:

```text
T1 = 100 seconds
T4 = 30 seconds

Speedup = 100 / 30
        = 3.33
```

The theoretical ideal for four resources would be:

```text
Speedup = 4
```

If the measured speedup is lower, some overhead or bottleneck is limiting scalability.

---

# 20. Parallel Efficiency

Parallel efficiency measures how effectively additional resources are being used.

\[
E(N) = \frac{S(N)}{N}
\]

For example:

```text
Speedup = 3.33
Resources = 4

Efficiency = 3.33 / 4
           = 0.8325
           = 83.25%
```

Higher efficiency generally indicates better scaling.

---

# 21. Performance Monitoring

Runtime alone does not explain why a workload performs well or poorly.

The cluster should also be monitored.

Important metrics include:

```text
CPU Utilization
       |
       +--> Are CPU cores being fully used?

Memory Utilization
       |
       +--> Is the application memory-bound?

MPI Processes
       |
       +--> How does process count affect scaling?

OpenMP Threads
       |
       +--> How does thread count affect performance?

I/O
       |
       +--> Is data access becoming a bottleneck?

Runtime
       |
       +--> Is the simulation actually getting faster?
```

A monitoring stack can therefore look like:

```text
ASCOT5 Job
     |
     v
Compute Nodes
     |
     +---- CPU
     +---- Memory
     +---- Network
     +---- I/O
     |
     v
Prometheus
     |
     v
Grafana
     |
     v
Performance Analysis
```

---

# 22. Research Questions

The following questions can be used to guide the HPC investigation.

### RQ1 — CPU Scaling

> How does ASCOT5 execution time scale as the number of CPU cores increases?

### RQ2 — MPI Scaling

> What effect does MPI process count have on ASCOT5 performance?

### RQ3 — OpenMP Scaling

> How does OpenMP thread count affect execution time and CPU utilization?

### RQ4 — Workload Scaling

> How does increasing the number of simulation markers affect runtime and memory usage?

### RQ5 — Resource Utilization

> What is the relationship between CPU utilization and ASCOT5 simulation performance?

### RQ6 — Bottleneck Analysis

> What performance bottlenecks limit ASCOT5 scaling on the HPC cluster?

---

# 23. Example Experiment

A basic experiment could keep the simulation configuration constant while changing the number of CPU resources.

```text
                Same ASCOT5 Input
                       |
       +---------------+---------------+
       |               |               |
       v               v               v
    1 Core          2 Cores         4 Cores
       |               |               |
       v               v               v
   Runtime          Runtime          Runtime
       |               |               |
       +---------------+---------------+
                       |
                       v
                Compare Results
```

A results table could look like:

| Cores | Runtime | Speedup | Efficiency | CPU Utilization |
|---:|---:|---:|---:|---:|
| 1 | 100 s | 1.00× | 100% | 95% |
| 2 | 55 s | 1.82× | 91% | 94% |
| 4 | 30 s | 3.33× | 83% | 93% |
| 8 | 17 s | 5.88× | 73% | 90% |

These numbers are **illustrative only**. Actual benchmark results must be measured from the cluster.

---

# 24. Project Goal

The goal of this project is to evaluate **ASCOT5 as a real scientific HPC workload**.

Rather than simply installing and running the application, the project investigates:

```text
ASCOT5
   |
   v
Scientific Workload
   |
   v
HPC Cluster
   |
   +--> CPU
   +--> Memory
   +--> MPI
   +--> OpenMP
   +--> I/O
   |
   v
Performance Measurements
   |
   +--> Runtime
   +--> Speedup
   +--> Efficiency
   +--> Utilization
   |
   v
Performance Analysis
```

The final objective is to understand **how efficiently the HPC cluster executes a real-world fusion-plasma simulation** and identify the factors that limit or improve performance.

---

# 25. Key Takeaway

ASCOT5 connects three important areas:

```text
       FUSION PHYSICS
             |
             v
          ASCOT5
             |
             v
       HPC COMPUTING
             |
             v
     PERFORMANCE ANALYSIS
```

ASCOT5 provides the **scientific workload**.

MPI, OpenMP and SIMD provide **parallel computation**.

Slurm provides **job scheduling**.

Prometheus and Grafana provide **performance monitoring**.

HDF5 provides **scientific data storage**.

Together, these technologies allow the project to investigate how modern HPC systems can support computationally intensive fusion research.

> **The purpose of this project is not simply to make ASCOT5 run. It is to investigate how effectively an HPC system can execute a real scientific workload and how computational resources affect its performance.**

---

# ASCOT5 Performance Bottlenecks

## Overview

ASCOT5 is a high-performance particle orbit-following application used in fusion plasma physics and engineering.

Because ASCOT5 can simulate large numbers of computational particles, it can place significant demands on CPU resources, memory, communication and storage.

The purpose of this investigation is to identify the potential performance bottlenecks when running ASCOT5 on an HPC cluster.

> **The bottleneck should not be assumed beforehand. It must be identified through performance measurements and benchmarking.**

---

## 1. CPU Computation

CPU computation is one of the main potential bottlenecks in ASCOT5.

The application repeatedly performs numerical calculations for simulated particles, including particle motion, field calculations, transport and interactions.

```text
Millions of Markers
        |
        v
Particle Calculations
        |
        v
Field Calculations
        |
        v
Transport / Interaction Calculations
        |
        v
Update Particle State
        |
        v
Repeat

## References

- ASCOT5 — Aalto University / VTT  
  https://github.com/ascot4fusion/ascot5

- ASCOT5 Python package configuration  
  https://github.com/ascot4fusion/ascot5/blob/main/pyproject.toml

- HDF5  
  https://github.com/HDFGroup/hdf5

---

## Project Status

**Status:** In Progress




### Current focus

- [ ] ASCOT5 installation
- [ ] Validate basic ASCOT5 execution
- [ ] Configure MPI
- [ ] Configure OpenMP
- [ ] Run baseline simulation
- [ ] Establish benchmark workload
- [ ] Measure CPU utilization
- [ ] Measure memory utilization
- [ ] Perform core/thread scaling
- [ ] Perform MPI scaling
- [ ] Calculate speedup
- [ ] Calculate parallel efficiency
- [ ] Identify performance bottlenecks
- [ ] Visualize benchmark results
- [ ] Document findings
