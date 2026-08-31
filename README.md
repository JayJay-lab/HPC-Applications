# HPC-Applications
## ASCOT5

ASCOT5 is a test-particle orbit-following code for solving minority species’ distribution functions, transport, and losses in tokamaks and stellarators. For questions related to the code or physics, please join our Slack channel.

## Features

ASCOT5 is a test-particle orbit-following code for computing particle orbits in 3D geometry. The output includes particle orbits, phase-space distributions, transport coefficients, and wall loads. ASCOT5 is frequently applied to study fast ions, impurities, neutrals, and runaway electrons in tokamaks and stellarators. Particle orbits are either solved fully, i.e. including the gyro-motion, or in a reduced picture where only the guiding-center trajectory is traced. The code is extensively parallelized and optimized to support simulations with more than ten million markers.

The code is implemented in C and consists of a main program and a library. Simulation input and output is stored in HDF5 format. All pre- and post-processing is done via the Python interface a5py. In addition the repository also contain several codes that supplement the orbit-following simulations.

The repository is maintained by Aalto University and VTT Technical Research Centre of Finland.

## Requirements

Install the requirements or use the module system:

C compiler (Intel)
HDF5
OpenMP
MPI
Python3.10



##  Intel oneAPI Toolkits — Maximum Performance ( C compiler and MPI)

Intel's oneAPI Toolkit is a comprehensive collection of compilers, math libraries, and profiling tools developed and maintained by Intel. The key components for HPL benchmarking are:

| Component | Purpose |
|---|---|
| **Intel C/C++ Compiler (`icx`)** | Generates highly optimized machine code for Intel CPUs, often outperforming GCC for vectorizable workloads |
| **Intel Math Kernel Library (MKL)** | Intel's BLAS implementation, specifically tuned for Intel microarchitectures using AVX-512, VNNI, and AMX instruction sets |
| **Intel MPI** | Intel's MPI implementation, tuned for both shared-memory and network communication patterns on Intel hardware |

> **⚠️ Time Warning:** The Base and HPC toolkit offline installers are each several gigabytes. Allow significant download and installation time. Skip this section if you have fallen behind the recommended pace — you can return to it.

---

### Step 1: Install Optional GUI Prerequisites

These packages enable Intel's VTune Profiler graphical interface (optional but useful for performance analysis):

```bash
sudo apt install -y libdrm2 libgtk-3-0 libnotify4 xdg-utils \
    libxcb-dri3-0 libgbm1 libatspi2.0-0
```

---

### Step 2: Download the Intel oneAPI Offline Installers

Download both the Base Toolkit and the HPC Toolkit into your home directory. These are large files — run these in a persistent session (use `tmux` or `screen` to prevent disconnection from interrupting the download):

**Intel oneAPI Base Toolkit (includes MKL and `icx`):**

```bash
cd ~
wget https://registrationcenter-download.intel.com/akdlm/IRC_NAS/9a98af19-1c68-46ce-9fdd-e249240c7c42/l_BaseKit_p_2024.2.0.634_offline.sh
```

**Intel oneAPI HPC Toolkit (includes Intel MPI and `ifort`):**

```bash
wget https://registrationcenter-download.intel.com/akdlm/IRC_NAS/d4e49548-1492-45c9-b678-8268cb0f1b05/l_HPCKit_p_2024.2.0.635_offline.sh
```

---

### Step 3: Make the Installer Scripts Executable

```bash
chmod +x l_BaseKit_p_2024.2.0.634_offline.sh
chmod +x l_HPCKit_p_2024.2.0.635_offline.sh
```

---

### Step 4: Run the Base Toolkit Installer

```bash
./l_BaseKit_p_2024.2.0.634_offline.sh -a --cli --eula accept
```

| Flag | Meaning |
|---|---|
| `-a` | Pass subsequent arguments to the installer engine |
| `--cli` | Run in Command Line Interface mode (no graphical window required) |
| `--eula accept` | Automatically accept the End User License Agreement |

The installer will display CLI text prompts. Navigate through them and confirm the installation. By default, Intel oneAPI is installed into `~/intel/oneapi/`.

---

### Step 5: Run the HPC Toolkit Installer

```bash
./l_HPCKit_p_2024.2.0.635_offline.sh -a --cli --eula accept
```

Again, navigate the CLI prompts and confirm.

---

### Step 6: Configure Your Environment for Intel oneAPI

The `setvars.sh` script sets up all required environment variables for the Intel compiler suite in one step:

```bash
source ~/intel/oneapi/setvars.sh
```

You will see output confirming that components like `mpiicx`, `ifort`, `mkl`, and `mpi` have been loaded. To apply this configuration automatically every time you log in:

```bash
echo 'source ~/intel/oneapi/setvars.sh' >> ~/.profile
```

---

### Step 7: Set Up Intel Lmod Modulefiles (Optional but Recommended)

If you successfully installed Lmod in Section 3.2, Intel oneAPI can register itself as loadable modules:

```bash
cd ~/intel/oneapi/
./modulefiles-setup.sh
```

Make the newly created modulefiles available to Lmod:

```bash
ml use $HOME/modulefiles
```

Verify the modules appear:

```bash
ml avail
```

You should see Intel compiler, MKL, and MPI modules listed. You can now load Intel tools with:

```bash
ml intel/2024.2
ml mpi/2024.2
ml mkl/2024.2
```

---


# HDF5

```bash

sudo apt update && sudo apt install -y libhdf5-openmpi-dev
```

# Python 3.10
```bash
```
