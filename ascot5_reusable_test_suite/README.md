# ASCOT5 HPC Application

A reusable, data-driven ASCOT5 workflow for running fusion-particle simulations on an MPI cluster, collecting results, and generating visualisations for performance analysis.

## Contents

- [Overview](#overview)
- [Why ASCOT5 is useful for HPC](#why-ascot5-is-useful-for-hpc)
- [Project structure](#project-structure)
- [Requirements](#requirements)
- [Install ASCOT5](#install-ascot5)
- [Configure the cluster](#configure-the-cluster)
- [Run simulations](#run-simulations)
- [Add a new test](#add-a-new-test)
- [Outputs](#outputs)
- [Visualisation](#visualisation)
- [Troubleshooting](#troubleshooting)

---

## Overview

[ASCOT5](https://github.com/ascot4fusion/ascot5) is a test-particle orbit-following code used to study particle motion, transport, collisions, and losses in magnetic-confinement fusion devices such as tokamaks and stellarators.

A typical simulation uses:

```text
Magnetic field
      +
Plasma parameters
      +
Reactor / wall geometry
      +
Particle properties
      |
      v
   ASCOT5
      |
      v
Particle trajectories
Energy evolution
Collisions
Wall interactions
      |
      v
Diagnostics + performance data
```

A **marker** represents a simulated particle. Many marker calculations can be performed independently, making ASCOT5 suitable for MPI, OpenMP, and SIMD/vectorised execution.

## Why ASCOT5 is useful for HPC

ASCOT5 can use several levels of parallelism:

```text
MPI processes
      |
OpenMP threads
      |
SIMD / vector operations
      |
Particle calculations
```

The workload is mainly computational, but memory can become important when using:

- Large magnetic-field inputs
- 3D wall geometry
- Large marker populations
- Distribution functions
- Diagnostic and output data

The HDF5 file can contain multiple inputs and simulation results. This makes ASCOT5 useful for repeatable experiments, parameter scans, and performance comparisons.

---

## Project structure

```text
ascot5-reusable/
├── README.md
├── ascot_tests.json          # Test data and configuration
├── run_ascot_tests.py        # Reusable simulation runner
└── runs/                     # Created automatically
    ├── baseline/
    │   ├── ascot.h5
    │   ├── input_summary.txt
    │   ├── output_summary.txt
    │   └── visualisations/
    └── more_markers/
        ├── ascot.h5
        ├── input_summary.txt
        ├── output_summary.txt
        └── visualisations/
```

> Each test is stored in its own directory. This prevents new experiments from overwriting earlier results.

---

# 1. Requirements

The project environment uses:

- Ubuntu 24.04
- Python 3.10+; Python 3.12 is supported by the project environment
- Intel oneAPI compiler and Intel MPI
- HDF5
- OpenMP
- ASCOT5 and `a5py`
- NumPy, SciPy, h5py, unyt, Matplotlib, and Plotly

Install the basic system packages:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-dev \
    libhdf5-serial-dev hdf5-tools
```

Verify Python and HDF5:

```bash
python3 --version
h5dump --version
h5cc -showconfig
```

## Intel oneAPI

Load Intel oneAPI before using Intel MPI or the Intel compiler:

```bash
source ~/intel/oneapi/setvars.sh
```

To load it automatically for future sessions:

```bash
echo 'source ~/intel/oneapi/setvars.sh' >> ~/.profile
```

If your cluster uses Lmod, load the appropriate Intel compiler, MPI, and MKL modules instead.

---

# 2. Install ASCOT5

Clone the source repository:

```bash
cd ~
git clone https://github.com/ascot4fusion/ascot5.git
```

Create and activate the virtual environment:

```bash
python3 -m venv ~/ascot-env
source ~/ascot-env/bin/activate
```

Install `a5py` and compile the ASCOT5 executables:

```bash
cd ~/ascot5
pip install --upgrade pip
pip install -e .
make ascot5_main -j MPI=1
make libascot -j MPI=1
```

The runner expects the main executable at:

```text
/home/ubuntu/ascot5/build/ascot5_main
```

If your installation is in another location, update `ascot_executable` in `ascot_tests.json`.

---

# 3. Configure the text editor

ASCOT5 options can be edited with `nano` or `vim`. To make `nano` the default editor:

```bash
echo 'export EDITOR=/usr/bin/nano' >> ~/.bashrc
source ~/.bashrc
```

---

# 4. Configure MPI networking

The Intel MPI process manager, Hydra, requires TCP connectivity between the cluster nodes.

In the current cluster, the headnode firewall uses an `hn_table` nftables chain with a default-drop policy. The MPI port range used by this project is:

```text
40000-40100
```

Inspect the firewall before changing it:

```bash
sudo nft list ruleset
sudo nft list chain inet hn_table hn_tcp_chain
sudo systemctl status nftables
```

If the cluster uses the same firewall structure, the required rules may look like:

```bash
sudo nft add rule inet hn_table hn_tcp_chain tcp dport 40000-40100 accept
sudo nft add rule inet hn_table hn_udp_chain udp dport 40000-40100 accept
```

Do **not** copy these commands blindly to another cluster. Confirm the table, chain names, interface, and persistent configuration first.

The runner uses these environment variables:

```bash
export I_MPI_HYDRA_IFACE=ens37
export I_MPI_PORT_RANGE=40000:40100
export HDF5_USE_FILE_LOCKING=FALSE
```

Change `ens37` if your cluster uses a different network interface.

Before debugging MPI, test the network path with a simple TCP listener:

```bash
# On the receiving node
nc -l -p 40000 -v

# From another node
nc -zv -w2 <node-ip> 40000
```

---

# 5. Install Jupyter and visualisation tools

Inside the ASCOT5 virtual environment:

```bash
pip install jupyter matplotlib plotly h5py unyt
ipython kernel install --user --name=ascotenv
```

Start Jupyter:

```bash
jupyter-notebook
```

The ASCOT5 tutorials are located at:

```bash
cd ~/ascot5/doc/tutorials
```

---

# 6. Data-driven test runner

The main idea is to keep the Python runner generic and put experiment-specific values in `ascot_tests.json`.

```text
ascot_tests.json
      |
      v
run_ascot_tests.py
      |
      +--> Create ASCOT5 inputs
      +--> Generate markers
      +--> Run MPI simulation
      +--> Read HDF5 results
      +--> Generate summaries
      +--> Generate visualisations
```

## Run one test

Activate the environment and move to the project directory:

```bash
source ~/ascot-env/bin/activate
cd ~/ascot5-reusable
```

Run a named test:

```bash
python3 run_ascot_tests.py --test baseline
```

## List available tests

```bash
python3 run_ascot_tests.py --list
```

## Run all tests

```bash
python3 run_ascot_tests.py --test all
```

## Use another configuration file

```bash
python3 run_ascot_tests.py \
    --config another_tests.json \
    --test all
```

> Use the exact command-line options shown by `python3 run_ascot_tests.py --help` if your local runner version differs.

---

# 7. Add a new test

Open the data file:

```bash
nano ascot_tests.json
```

Add another test entry. For example:

```json
{
  "name": "more_markers",
  "workflow": "afsi_slowingdown",
  "markers": 10000,
  "birth_energy_eV": 3520000.0,
  "seed": 42,
  "output_prefix": "more_markers"
}
```

The important principle is:

- Change values in the JSON file.
- Keep the Python runner unchanged.
- Run the test by name.
- Compare the generated results.

Useful parameters for a benchmark study include:

| Parameter | What it changes |
|---|---|
| `markers` | Number of simulated particles |
| `birth_energy_eV` | Initial particle energy |
| Plasma density | Slowing-down rate and collision behaviour |
| Plasma temperature | Collision and thermalisation behaviour |
| Maximum mileage | Maximum tracked particle distance |
| CPU time limit | Maximum simulation CPU time |
| MPI processes | Number of distributed processes |
| OpenMP threads | Threads used by each MPI process |
| Random seed | Reproducibility of stochastic sampling |

The exact parameter names supported by the runner are defined in `ascot_tests.json` and `run_ascot_tests.py`.

---

# 8. Outputs

A completed test should produce a directory containing files such as:

```text
runs/<test-name>/
├── ascot.h5
├── input_summary.txt
├── output_summary.txt
└── visualisations/
    ├── energy_histogram.png
    ├── mileage_histogram.png
    └── particle_distribution_3d.html
```

## HDF5 file

`ascot.h5` stores the simulation inputs and results. It should be opened through `a5py` when possible rather than manually navigating the raw HDF5 structure.

## Input summary

`input_summary.txt` records the configuration used to create the simulation.

## Output summary

`output_summary.txt` records useful quantities such as:

- Number of markers processed
- Minimum and mean final energy
- Thermalised marker count
- Mean distance travelled
- Simulation status

## Visualisations

The runner can generate:

- Energy distributions
- Mileage distributions
- Interactive 3D particle plots
- Additional diagnostic plots added to the runner later

---

# 9. Comparing multiple tests

For an HPC performance study, keep the physics setup constant while changing one variable at a time.

Example:

```text
baseline       -> 1,000 markers
more_markers   -> 10,000 markers
large_test     -> 100,000 markers
```

Compare:

- Total runtime
- Runtime per marker
- MPI scaling
- OpenMP scaling
- CPU utilisation
- Memory usage
- Number of completed markers
- Energy and thermalisation behaviour

A useful rule is to change only one major parameter between tests. This makes it easier to explain why performance or physical results changed.

---

# 10. Troubleshooting

## `ValueError: Unknown template: plasma`

Use the ASCOT5 template name:

```python
a5.data.create_input("plasma_1D", ...)
```

The plasma input also needs the correct profile keys, such as `edensity`, `etemperature`, `idensity`, and `itemperature`, depending on the ASCOT5 tutorial/API version.

## `AttributeError: 'tuple' object has no attribute 'abscissa_edges'`

Some ASCOT5 AFSI calls return a tuple. Unpack the primary distribution before using it:

```python
result = a5.afsi.thermal(...)
alphadist = result[0] if isinstance(result, (tuple, list)) else result
```

## MPI reports `bstrap_proxy` or connection errors

Check the following in order:

1. Nodes can SSH to one another without a password prompt.
2. The correct network interface is used.
3. The MPI port range is allowed by the firewall.
4. The same Intel MPI environment is loaded on all nodes.
5. The ASCOT5 executable and required libraries are available on all worker nodes.
6. `HDF5_USE_FILE_LOCKING=FALSE` is set when using shared HDF5 files, if required by your setup.

Test MPI separately:

```bash
mpirun -hosts compute1,compute2 -np 2 hostname
```

## Check the executable

```bash
ls -lh ~/ascot5/build/ascot5_main
ldd ~/ascot5/build/ascot5_main
```

## Check the active Intel MPI

```bash
which mpirun
which mpiexec
mpirun --version
```

---

# 11. Useful references

- [ASCOT5 source repository](https://github.com/ascot4fusion/ascot5)
- [ASCOT5 tutorials](https://github.com/ascot4fusion/ascot5/tree/main/doc/tutorials)
- [HDF5 documentation](https://www.hdfgroup.org/solutions/hdf5/)
- [Intel oneAPI documentation](https://www.intel.com/content/www/us/en/developer/tools/oneapi/overview.html)

---

## Project note

ASCOT5 is a scientific simulation application, not a fusion reactor. It is used to predict particle behaviour inside fusion devices and to help researchers study confinement, transport, losses, and reactor-component loads.
