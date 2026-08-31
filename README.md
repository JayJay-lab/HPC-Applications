# HPC-Applications
## ASCOT5

ASCOT5 is a test-particle orbit-following code for solving minority species’ distribution functions, transport, and losses in tokamaks and stellarators. For questions related to the code or physics, please join our Slack channel.


#ASCOT in the real world 

The real-life purpose of ASCOT5 is to help scientists and engineers design, understand, and improve nuclear fusion reactors.

It does this by simulating what happens to charged particles inside a fusion device such as a tokamak or stellarator.

For example, researchers can use ASCOT to study:

How well particles are confined by the reactor's magnetic fields
Where energetic particles travel
How much energy particles lose
What happens when particles hit the reactor walls
How much heat and particle load reaches reactor components
How plasma impurities move through the reactor

This matters because a fusion reactor needs to keep the extremely hot plasma confined while protecting the reactor's physical components.


```bash
Engineer designs magnetic field
            ↓
       ASCOT simulation
            ↓
Tracks millions of particles
            ↓
Predicts their trajectories
            ↓
Finds where particles escape
            ↓
Predicts heat/load on reactor walls
            ↓
Engineer modifies reactor design
```
Note well!!!
So ASCOT is not itself a fusion reactor. It is a scientific simulation tool used to predict what will happen inside fusion machines before engineers build, modify, or operate them.



# What does this application calculates

ASCOT5 is a particle-following fusion simulation code. You give it information such as:
```bash
Magnetic field
Plasma parameters
Reactor geometry / wall
Particle properties
       ↓
      ASCOT5
       ↓
Numerically calculate particle motion
       ↓
Particle trajectories + energy + collisions + wall interactions
       ↓
Statistics / diagnostics / physics results
```

A "marker" in ASCOT is essentially a simulated particle. ASCOT numerically advances these markers through the magnetic field and calculates what happens to them. The important point for HPC is that different markers can largely be simulated independently, which makes the problem highly parallelizable.

Note!!! 
it is running mathematical and numerical calculations continuously during the simulation.

#Is it CPU or memory intensive

ASCOT5 uses several levels of parallelism:
```bash
MPI processes
      ↓
OpenMP threads
      ↓
SIMD/vector operations
      ↓
Particle calculations
```

#  But memory can become important

ASCOT isn't simply "CPU only."

Some inputs can consume substantial memory, particularly things such as:

3D magnetic fields
3D wall geometry
distribution outputs
large numbers of simulation markers

The ASCOT documentation specifically notes that these can be memory-intensive inputs, and that MPI processes do not share memory.













## Features

ASCOT5 is a test-particle orbit-following code for computing particle orbits in 3D geometry. The output includes particle orbits, phase-space distributions, transport coefficients, and wall loads. ASCOT5 is frequently applied to study fast ions, impurities, neutrals, and runaway electrons in tokamaks and stellarators. Particle orbits are either solved fully, i.e. including the gyro-motion, or in a reduced picture where only the guiding-center trajectory is traced. The code is extensively parallelized and optimized to support simulations with more than ten million markers.

The code is implemented in C and consists of a main program and a library. Simulation input and output is stored in HDF5 format. All pre- and post-processing is done via the Python interface a5py. In addition the repository also contain several codes that supplement the orbit-following simulations.

The repository is maintained by Aalto University and VTT Technical Research Centre of Finland.


### BBNBI

Calculates beam birth profile and shinethrough from NBI geometry.

Can provide a NBI source for ASCOT5 slowing-down simulations.

### AFSI

Calculates fusion product source from thermal plasma and fast ion slowing-down distributions (as computed by ASCOT5).

For fusion neutronics, AFSI can be combined with Serpent.

### BioSaw

Calculates magnetic field based on a coil geometry.

Can provide a 3D field for ASCOT5 simulations.

### BMC

Backward Monte-Carlo simulation tool that can be thought as a time-reversed ASCOT5.

Effective tool for estimating FILD signals and wall loads on small but critical components.

Not yet fully complete.



## Processing data

#Data

The ASCOT5 HDF5 file, named ascot.h5 from here on out, contains all data required to run a simulation. All data is contained in a single file so that the results, and the inputs that produced them, are always kept together. The file is designed to hold multiple inputs (even of same type) and results of multiple simulations. One is encouraged to use a single file for the whole project or study.

The exact structure of the contents of the HDF5 file is not that relevent since it should always be accessed via the Python interface provided by a5py. When accessed via Python, the contents of the file as they appear are illustrated below:

```bash
data
├── bfield               # Magnetic field inputs
│   ├── B_2DS_7027705680 # Some 2D magnetic field data
│   ├── B_3DS_0890178582 # Some other 2D magnetic field data
│   └── ...              # Some other possible magnetic field data
│
├── efield               # Electric field inputs
│   └── ...
│
├── ...                  # Other inputs (wall, plasma, etc.)
│
├── run_892758002        # Results of a single simulation
├── run_992765110        # Results of another simulation
└── ...                  # Other possible results

```

The input data is divided into separate parent groups: one for the magnetic field inputs, one for the electric field inputs and so on. Each parent group can have multiple children which contain the actual input data. For example, one may have several plasma inputs that vary in density for a parameter scan or one can have a separate 2D and 3D magnetic fields for comparison. One of the children is always marked as active meaning that input will be used in the next simulation. The active input is used by default when interpolating the input data via the Python interface in pre- and postprocessing.

As for the results, one group is always marked as active (if any results exist) which by default is the result of the most recent simulation. Each input and result has a ten number string that is randomly generated when that data is written to the file. This QID (quasi unique identifier) is used to separate different inputs and results from one another. Each input and result also contains the date at which they were created, what type they are (e.g. 2D vs 3D tokamak magnetic field), and an optional description given by the user. It is strongly recommended to document your work using the description field which can also be used to conveniently access the data in postprocessing.

# Data access

No actual data is read during the initialization, so these objects are very light-weight and new instances can be created at will The contents of the file are accessed via Ascot.data, which is an instance of Ascot5IO, and it provides a “treeview” of the file which was illustrated in the previous section.

Inputs are divided to groups depending on what type of input data they provide. All magnetic field inputs are located in the bfield group, all electric field inputs in the efield group, and so on. All different input parent groups are instances of InputNode class



# 1. Requirements

Install the requirements or use the module system:

C compiler (Intel)
HDF5
OpenMP
MPI
Python3.10



##   Intel oneAPI Toolkits — Maximum Performance ( C compiler and MPI)

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


## HDF5

```bash

sudo apt update && sudo apt install -y libhdf5-openmpi-dev
```
verify 
```bash

which h5pcc || which h5pcc.openmpi
```
output /usr/bin/h5pcc

## Python 3.10
```bash

sudo apt update
sudo apt install -y python3.10 python3.10-venv python3.10-dev
```
```bash
python3.10 --version
```

# 2. Installing ASCOT5

## Download the source and set up the virtual environment:
```bash
git clone https://github.com/ascot4fusion/ascot5.git
python -m venv ascot-env
source activate ascot-env/bin/activate
```

## Install a5py and compile the executables which will be located at build/:

```bash
cd ascot5
pip install -e .
make ascot5_main -j MPI=1
make libascot -j MPI=1
```

##The simulation options are edited with the local text editor, which usually happens to be vim. Consider adding the following line to your .bashrc (or .bash_profile if working locally):

```bash
echo 'export EDITOR=/usr/bin/nano' >> ~/.bashrc
```






