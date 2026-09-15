#!/usr/bin/env python3
"""
Data-driven ASCOT5 multi-node test runner.

Edit ascot_tests.json to add/change test cases. The Python code should normally
not need to be changed for parameter scans.

Examples:
    python3 run_ascot_tests.py --list
    python3 run_ascot_tests.py --test slowingdown_baseline
    python3 run_ascot_tests.py --test all
    python3 run_ascot_tests.py --config ascot_tests.json --test more_markers
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import h5py
import numpy as np

# Compatibility for ASCOT/a5py environments that still reference np.in1d.
if not hasattr(np, "in1d"):
    np.in1d = np.isin

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import unyt

from a5py import Ascot
from a5py.ascot5io.marker import Marker
from a5py.ascot5io.options import Opt


def deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge dictionaries without modifying the originals."""
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def find_test(config: dict, name: str) -> dict:
    for test in config["tests"]:
        if test["name"] == name:
            return test
    names = ", ".join(item["name"] for item in config["tests"])
    raise ValueError(f"Unknown test '{name}'. Available tests: {names}")


def build_plasma(a5: Ascot, plasma: dict) -> None:
    rho = np.linspace(
        plasma["rho_min"], plasma["rho_max"], plasma["nrho"]
    ).reshape(-1, 1)

    vtor = np.zeros_like(rho)
    edens = np.full_like(rho, plasma["electron_density_m3"], dtype=float)
    etemp = np.full_like(rho, plasma["electron_temperature_eV"], dtype=float)
    idens = np.full((plasma["nrho"], len(plasma["anum"])),
                    plasma["ion_density_m3"], dtype=float)
    itemp = np.full_like(etemp, plasma["ion_temperature_eV"], dtype=float)

    edge_mask = rho[:, 0] > plasma["edge_rho_cutoff"]
    edens[edge_mask, :] = plasma["edge_electron_density_m3"]
    idens[edge_mask, :] = plasma["edge_ion_density_m3"]

    data = {
        "nrho": plasma["nrho"],
        "nion": len(plasma["anum"]),
        "rho": rho[:, 0],
        "vtor": vtor,
        "anum": np.asarray(plasma["anum"]),
        "znum": np.asarray(plasma["znum"]),
        "mass": np.asarray(plasma["mass_amu"]),
        "charge": np.asarray(plasma["charge"]),
        "edensity": edens,
        "etemperature": etemp,
        "idensity": idens,
        "itemperature": itemp,
    }

    a5.data.create_input(
        "plasma_1D",
        **data,
        desc=plasma["description"],
    )


def build_afsi(a5: Ascot, afsi: dict):
    ppar = np.linspace(
        afsi["ppar_min"], afsi["ppar_max"], afsi["nppar"]
    )
    pperp = np.linspace(
        afsi["pperp_min"], afsi["pperp_max"], afsi["npperp"]
    )

    result = a5.afsi.thermal(
        afsi["reaction"],
        nmc=afsi["nmc"],
        r=np.linspace(afsi["r_min"], afsi["r_max"], afsi["nr"]),
        phi=np.linspace(
            afsi["phi_min_deg"], afsi["phi_max_deg"], afsi["nphi"]
        ),
        z=np.linspace(afsi["z_min"], afsi["z_max"], afsi["nz"]),
        ppar1=ppar,
        ppar2=ppar,
        pperp1=pperp,
        pperp2=pperp,
    )
    # ASCOT5 versions may return a tuple/list for AFSI.
    return result[0] if isinstance(result, (tuple, list)) else result


def build_direct_markers(
    a5: Ascot,
    marker_cfg: dict,
    count: int,
    birth_energy_eV: float,
    seed: int,
) -> int:
    """Create simple direct guiding-center alpha markers without AFSI."""
    rng = np.random.default_rng(seed)
    mrk = Marker.generate("gc", n=count, species=marker_cfg["species"])

    if "energy" in mrk:
        mrk["energy"][:] = birth_energy_eV
    if "ekin" in mrk:
        mrk["ekin"][:] = birth_energy_eV
    if "pitch" in mrk:
        mrk["pitch"][:] = rng.uniform(
            marker_cfg["pitch_min"], marker_cfg["pitch_max"], len(mrk["ids"])
        )
    if "r" in mrk:
        mrk["r"][:] = marker_cfg["r_center_m"] + rng.uniform(
            -marker_cfg["r_half_width_m"],
            marker_cfg["r_half_width_m"],
            len(mrk["ids"]),
        )
    if "z" in mrk:
        mrk["z"][:] = rng.uniform(
            marker_cfg["z_min_m"],
            marker_cfg["z_max_m"],
            len(mrk["ids"]),
        )
    if "phi" in mrk:
        mrk["phi"][:] = rng.uniform(
            0.0, 2.0 * np.pi, len(mrk["ids"])
        )

    mrk["ids"][:] = np.arange(1, len(mrk["ids"]) + 1)
    a5.data.create_input(
        "gc",
        **mrk,
        desc=marker_cfg["description"],
    )
    return len(mrk["ids"])


def build_markers(
    a5: Ascot,
    marker_cfg: dict,
    afsi_dist,
    count: int,
    birth_energy_eV: float,
    seed: int,
) -> int:
    rng = np.random.default_rng(seed)

    rho_mrk = np.linspace(0.0, 0.5, 2)
    prob = np.full(2, 0.5)

    a5.input_init(bfield=True)
    markerdist = a5.markergen.rhoto5d(
        rho_mrk,
        prob,
        afsi_dist.abscissa_edges("r"),
        afsi_dist.abscissa_edges("phi"),
        afsi_dist.abscissa_edges("z"),
        afsi_dist.abscissa_edges("ekin"),
        afsi_dist.abscissa_edges("pitch"),
    )
    a5.input_free()

    # Use the AFSI distribution when creating markers, matching the existing
    # slowing-down workflow in the project.
    mrk, _, _ = a5.markergen.generate(
        count,
        marker_cfg["mass_amu"] * unyt.amu,
        marker_cfg["charge_e"] * unyt.e,
        4,
        2,
        afsi_dist,
        markerdist=markerdist,
        minweight=1e-10,
        return_dists=True,
    )

    # Make the birth energy and spatial/pitch distributions explicit so the
    # test data file controls the important benchmark parameters.
    if "energy" in mrk:
        mrk["energy"][:] = birth_energy_eV

    if "ekin" in mrk:
        mrk["ekin"][:] = birth_energy_eV

    if "pitch" in mrk:
        mrk["pitch"][:] = rng.uniform(
            marker_cfg["pitch_min"], marker_cfg["pitch_max"], len(mrk["ids"])
        )

    if "r" in mrk:
        mrk["r"][:] = (
            marker_cfg["r_center_m"]
            + rng.uniform(
                -marker_cfg["r_half_width_m"],
                marker_cfg["r_half_width_m"],
                len(mrk["ids"]),
            )
        )

    if "z" in mrk:
        mrk["z"][:] = rng.uniform(
            marker_cfg["z_min_m"],
            marker_cfg["z_max_m"],
            len(mrk["ids"]),
        )

    if "phi" in mrk:
        mrk["phi"][:] = rng.uniform(0.0, 2.0 * np.pi, len(mrk["ids"]))

    mrk["ids"][:] = np.arange(1, len(mrk["ids"]) + 1)

    a5.data.create_input(
        "gc",
        **mrk,
        desc=marker_cfg["description"],
    )
    return len(mrk["ids"])


def create_optional_inputs(a5: Ascot) -> None:
    """Inputs retained from the working slowing-down tutorial pipeline."""
    a5.data.create_input("wall rectangular")
    a5.data.create_input("E_TC")
    a5.data.create_input("N0_1D")
    a5.data.create_input("Boozer")
    a5.data.create_input("MHD_STAT")
    a5.data.create_input("asigma_loc")


def make_summary_and_plots(
    h5_path: Path,
    output_dir: Path,
    prefix: str,
    birth_energy_eV: float,
    elapsed_s: float,
) -> dict:
    with h5py.File(h5_path, "r") as handle:
        if "results" not in handle:
            raise RuntimeError("ASCOT5 produced no results group.")

        result_keys = [
            key for key in handle["results"].keys()
            if not key.startswith("afsi")
        ]
        if not result_keys:
            result_keys = list(handle["results"].keys())
        if not result_keys:
            raise RuntimeError("No ASCOT5 result was found.")

        run_key = result_keys[-1]
        end = handle["results"][run_key]["endstate"]
        r = end["r"][:]
        z = end["z"][:]
        phi = end["phi"][:]
        ekin = end["ekin"][:]
        mileage = end["mileage"][:]
        endcond = end["endcond"][:]

    thermalized = int(np.count_nonzero(ekin <= 20.0e3))
    particle_count = len(ekin)

    if particle_count == 0:
        raise RuntimeError("ASCOT5 returned zero particles in endstate.")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].hist(ekin * 1e-6, bins=50, edgecolor="black", alpha=0.75)
    axes[0].set_xlabel("Final Kinetic Energy [MeV]")
    axes[0].set_ylabel("Particle Count")
    axes[0].set_title("Final Energy Distribution")
    axes[0].grid(True, alpha=0.3)

    axes[1].hist(mileage, bins=50, edgecolor="black", alpha=0.75)
    axes[1].set_xlabel("Tracked Mileage [m]")
    axes[1].set_ylabel("Particle Count")
    axes[1].set_title("Particle Mileage")
    axes[1].grid(True, alpha=0.3)

    fig.tight_layout()
    hist_path = output_dir / f"{prefix}_2d_histograms.png"
    fig.savefig(hist_path, dpi=200)
    plt.close(fig)

    phi_rad = (
        phi if np.max(np.abs(phi)) <= 2 * np.pi
        else np.deg2rad(phi)
    )
    phi_rad = np.mod(phi_rad, 2 * np.pi)
    x = r * np.cos(phi_rad)
    y = r * np.sin(phi_rad)

    fig3d = go.Figure()
    fig3d.add_trace(
        go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode="markers",
            marker=dict(
                size=3,
                color=ekin * 1e-6,
                colorscale="Turbo",
                colorbar=dict(title="Energy [MeV]"),
                opacity=0.8,
            ),
            text=[
                f"E: {energy * 1e-6:.3f} MeV<br>End: {condition}"
                for energy, condition in zip(ekin, endcond)
            ],
            hoverinfo="text+x+y+z",
            name="Endstate particles",
        )
    )
    fig3d.update_layout(
        title=f"{prefix}: ASCOT5 Endstate Distribution",
        scene=dict(
            xaxis_title="X [m]",
            yaxis_title="Y [m]",
            zaxis_title="Z [m]",
            aspectmode="data",
        ),
        template="plotly_dark",
        margin=dict(l=0, r=0, b=0, t=40),
    )
    html_path = output_dir / f"{prefix}_3d_browser.html"
    fig3d.write_html(html_path)

    summary = {
        "result_key": run_key,
        "particles_processed": particle_count,
        "birth_energy_MeV": birth_energy_eV * 1e-6,
        "minimum_energy_MeV": float(np.min(ekin) * 1e-6),
        "mean_end_energy_MeV": float(np.mean(ekin) * 1e-6),
        "thermalized_count_E_le_20keV": thermalized,
        "thermalized_percent_E_le_20keV": float(100.0 * thermalized / particle_count),
        "mean_mileage_m": float(np.mean(mileage)),
        "wall_or_other_end_condition_count": int(np.count_nonzero(endcond)),
        "elapsed_seconds_python_wrapper": elapsed_s,
    }

    with (output_dir / f"{prefix}_summary.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(summary, handle, indent=2)

    with (output_dir / f"{prefix}_summary.txt").open(
        "w", encoding="utf-8"
    ) as handle:
        handle.write(f"=== {prefix.upper()} RESULTS ===\n")
        for key, value in summary.items():
            handle.write(f"{key}: {value}\n")

    return summary


def write_input_summary(
    output_dir: Path,
    test: dict,
    effective: dict,
    marker_count: int,
) -> None:
    text = [
        "=== ASCOT5 TEST INPUT CONFIGURATION ===",
        f"Test: {test['name']}",
        f"Description: {test.get('description', '')}",
        f"Markers: {marker_count}",
        f"Birth energy [MeV]: {test['birth_energy_eV'] * 1e-6}",
        f"Random seed: {test.get('seed', 0)}",
        f"Electron density [m^-3]: {effective['plasma']['electron_density_m3']}",
        f"Electron temperature [eV]: {effective['plasma']['electron_temperature_eV']}",
        f"Ion density [m^-3]: {effective['plasma']['ion_density_m3']}",
        f"Ion temperature [eV]: {effective['plasma']['ion_temperature_eV']}",
        f"Maximum mileage [m]: {effective['simulation_options']['ENDCOND_MAX_MILEAGE']}",
        "",
        "The complete machine-readable configuration is stored in the JSON file",
        "used to launch this test.",
        "",
    ]
    (output_dir / "input_summary.txt").write_text(
        "\n".join(text), encoding="utf-8"
    )


def run_one(config: dict, test: dict) -> dict:
    root = Path(config["paths"]["output_root"])
    output_dir = root / test["name"]
    output_dir.mkdir(parents=True, exist_ok=True)

    effective = {
        "plasma": copy.deepcopy(config["common"]["plasma"]),
        "afsi": copy.deepcopy(config["common"]["afsi"]),
        "marker_birth": copy.deepcopy(config["common"]["marker_birth"]),
        "simulation_options": copy.deepcopy(
            config["common"]["simulation_options"]
        ),
    }
    effective = deep_merge(effective, test.get("overrides", {}))

    h5_path = output_dir / "ascot.h5"

    # Remove only this test's old output, never another test's data.
    if h5_path.exists():
        h5_path.unlink()

    print(f"\n=== TEST: {test['name']} ===")
    print(test.get("description", ""))
    print(f"Output: {output_dir}")

    print("[1/5] Building ASCOT5 inputs...")
    a5 = Ascot(str(h5_path), create=True)

    field = config["common"]["field"]
    a5.data.create_input(
        field["template"],
        desc=field["description"],
    )
    build_plasma(a5, effective["plasma"])
    create_optional_inputs(a5)

    workflow = test.get("workflow", "afsi_slowingdown")
    if workflow == "afsi_slowingdown":
        print("[2/5] Building AFSI source and markers...")
        afsi_dist = build_afsi(a5, effective["afsi"])
        marker_count = build_markers(
            a5,
            effective["marker_birth"],
            afsi_dist,
            int(test["markers"]),
            float(test["birth_energy_eV"]),
            int(test.get("seed", 0)),
        )
    elif workflow == "direct_alpha":
        print("[2/5] Building direct alpha markers...")
        marker_count = build_direct_markers(
            a5,
            effective["marker_birth"],
            int(test["markers"]),
            float(test["birth_energy_eV"]),
            int(test.get("seed", 0)),
        )
    else:
        raise ValueError(
            f"Unknown workflow '{workflow}'. "
            "Supported workflows: afsi_slowingdown, direct_alpha"
        )

    opt = Opt.get_default()
    opt.update(effective["simulation_options"])
    a5.data.create_input("opt", **opt, desc=test["name"])

    write_input_summary(output_dir, test, effective, marker_count)

    print(f"   -> Created {marker_count} markers.")
    print(f"   -> HDF5 input: {h5_path}")

    print("[3/5] Running ASCOT5 with MPI...")
    mpi = config["mpi"]
    hosts = ",".join(mpi["hosts"])
    cmd = [
        "mpirun",
        "-hosts", hosts,
        "-np", str(mpi["np"]),
        "-wdir", str(output_dir.resolve()),
        "-genv", "HDF5_USE_FILE_LOCKING", "FALSE",
        "-genv", "OMP_NUM_THREADS", str(mpi["omp_threads"]),
        "-genv", "I_MPI_PIN", "1",
        "-genv", "I_MPI_PIN_DOMAIN", "omp",
        config["paths"]["ascot_binary"],
        "--d=" + test["name"],
    ]

    env = os.environ.copy()
    env["HDF5_USE_FILE_LOCKING"] = "FALSE"
    env["I_MPI_HYDRA_IFACE"] = mpi["hydra_iface"]
    env["I_MPI_PORT_RANGE"] = mpi["port_range"]

    started = time.perf_counter()
    result = subprocess.run(cmd, env=env)
    elapsed = time.perf_counter() - started

    (output_dir / "mpi_command.txt").write_text(
        " ".join(cmd) + "\n", encoding="utf-8"
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Test '{test['name']}' failed with return code "
            f"{result.returncode}. Output was kept in {output_dir}."
        )

    print(f"   -> MPI run completed in {elapsed:.3f} s.")

    print("[4/5] Creating plots and result summaries...")
    summary = make_summary_and_plots(
        h5_path,
        output_dir,
        test["output_prefix"],
        float(test["birth_energy_eV"]),
        elapsed,
    )

    print("[5/5] Test complete.")
    print(
        f"   -> Mean end energy: "
        f"{summary['mean_end_energy_MeV']:.4f} MeV"
    )
    print(
        f"   -> Thermalized (<=20 keV): "
        f"{summary['thermalized_percent_E_le_20keV']:.1f}%"
    )

    return {
        "name": test["name"],
        "status": "PASS",
        "elapsed_seconds": elapsed,
        "output_dir": str(output_dir),
        **summary,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run data-driven ASCOT5 test cases."
    )
    parser.add_argument(
        "--config",
        default="ascot_tests.json",
        help="Path to JSON configuration file.",
    )
    parser.add_argument(
        "--test",
        default="all",
        help="Test name or 'all'.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available tests and exit.",
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}", file=sys.stderr)
        return 2

    try:
        config = load_config(config_path)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid JSON: {exc}", file=sys.stderr)
        return 2

    if args.list:
        for item in config["tests"]:
            print(f"- {item['name']}: {item.get('description', '')}")
        return 0

    selected = (
        config["tests"]
        if args.test == "all"
        else [find_test(config, args.test)]
    )

    results = []
    overall_failed = False

    for test in selected:
        try:
            results.append(run_one(config, test))
        except Exception as exc:
            overall_failed = True
            print(
                f"\nERROR: {test['name']}: {exc}",
                file=sys.stderr,
            )
            results.append({
                "name": test["name"],
                "status": "FAIL",
                "error": str(exc),
            })

    root = Path(config["paths"]["output_root"])
    root.mkdir(parents=True, exist_ok=True)
    report_path = root / "test_report.json"
    report_path.write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )

    print("\n=== TEST SUITE SUMMARY ===")
    for result in results:
        print(f"{result['name']}: {result['status']}")

    print(f"Report: {report_path}")

    return 1 if overall_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
