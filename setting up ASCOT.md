# ASCOT5
# 1. Requirements

## Install the requirements or use the module system:

### C compiler (Intel)
### HDF5
### OpenMP
### MPI (Intel)
### Python3.10


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
### Step 3. Make sure u are using all of your space
```bash
df -h
lsblk
sudo growpart /dev/sda 3
sudo pvresize /dev/sda3
sudo lvextend -l +100%FREE -r /dev/mapper/ubuntu--vg-ubuntu--lv
```
### Step 4: Make the Installer Scripts Executable

```bash
chmod +x l_BaseKit_p_2024.2.0.634_offline.sh
chmod +x l_HPCKit_p_2024.2.0.635_offline.sh
```

---

### Step 5: Run the Base Toolkit Installer

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

### Step 6: Run the HPC Toolkit Installer

```bash
./l_HPCKit_p_2024.2.0.635_offline.sh -a --cli --eula accept
```

Again, navigate the CLI prompts and confirm.

---

### Step 7: Configure Your Environment for Intel oneAPI

The `setvars.sh` script sets up all required environment variables for the Intel compiler suite in one step:

```bash
source ~/intel/oneapi/setvars.sh
```

You will see output confirming that components like `mpiicx`, `ifort`, `mkl`, and `mpi` have been loaded. To apply this configuration automatically every time you log in:

```bash
echo 'source ~/intel/oneapi/setvars.sh' >> ~/.profile
```

---

### Step 8: Set Up Intel Lmod Modulefiles (Optional but Recommended)

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

sudo apt update && sudo apt install -y libhdf5-serial-dev hdf5-tools
```
verify 
```bash

h5dump --version
h5cc -showconfig
```
If h5dump returns a version number, the tools are installed and ready to use

Check the Package Status via dpkg
```bash
dpkg -l | grep -E "libhdf5-serial-dev|hdf5-tools"
```
expected output
```bash
ii  hdf5-tools                    1.14.3-1ubuntu5   amd64  HDF5 Software Collection - Tools
ii  libhdf5-serial-dev            1.14.3-1ubuntu5   amd64  HDF5 - Serial Development files
```
if the second part is not in output it might affect the python application from getting the data since all data is nested 
```bash # Tell your shell where the HDF5 libraries and headers are located
export HDF5_DIR=/usr/lib/x86_64-linux-gnu/hdf5/serial
export HDF5_INCLUDEDIR=/usr/include/hdf5/serial

# (Optional) Add them to your profile so you don't lose them on reboot
echo 'export HDF5_DIR=/usr/lib/x86_64-linux-gnu/hdf5/serial' >> ~/.bashrc
echo 'export HDF5_INCLUDEDIR=/usr/include/hdf5/serial' >> ~/.bashrc
```
Verify Header and Library Files
```bash
find /usr/include -name "hdf5.h"

```
This should print a path like 
```bash
/usr/include/hdf5/serial/hdf5.h
output /usr/bin/h5pcc
```

If you are running on multiple nodes then to ensure worker nodes can resolve the dynamic HDF5 libraries at runtime:

On each worker node (or via an SSH loop):

```bash
sudo apt update && sudo apt install -y libhdf5-103-1  # or libhdf5-serial-100+ depending on Ubuntu release
# Quick catch-all for runtime libraries only (no compiler headers):
sudo apt install -y "libhdf5-*" --no-install-recommends
```

## Python 3.12
```bash

sudo apt update
sudo apt install -y python3 python3-venv python3-dev
```
```bash
python3 --version
```


## ASCOT5 simulation options can be edited using a text editor such as nano or vim. These editors allow you to modify configuration files directly from the Ubuntu terminal.
To make nano your default text editor, run the following command:

```bash
echo 'export EDITOR=/usr/bin/nano' >> ~/.bashrc
```
Then reload your Bash configuration:
```bash
source ~/.bashrc
```

