
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from skfem import asm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

import fem_history_fem as base

OUTPUT_DIR = ROOT / "figures"
OUTPUT_DIR.mkdir(exist_ok=True)

ALPHA_VALUES = np.array(
    [0.0, 0.5, 1.0, 1.5, 2.0]
)

# The baseline model is linear elastic.
# Alpha is a hypothetical eigenstrain multiplier,
# not an experimentally calibrated parameter.

history_force = (
    base.f_history_5000
    + base.f_history_increment_7000
)

history_displacement = (
    base.u_history_5000
    + base.u_history_increment_7000
)

rows = []

for alpha in ALPHA_VALUES:
    # Method 1: linear superposition
    u_superposed = (
        base.u_pressure
        + alpha * history_displacement
    )

    # Method 2: independently solve combined load
    combined_force = (
        base.f_pressure
        + alpha * history_force
    )
    u_direct = base.solve_system(combined_force)

    max_error_m = float(
        np.max(np.abs(u_direct - u_superposed))
    )

    axial_mm, radial_mm = base.extract_deformation(
        u_direct
    )

    rows.append({
        "alpha": float(alpha),
        "axial_shortening_mm": axial_mm,
        "radial_contraction_mm": radial_mm,
        "superposition_error_m": max_error_m,
        "current_pressure_psi": base.CURRENT_PRESSURE_PSI,
        "young_modulus_GPa_assumed": base.E / 1e9,
        "poisson_ratio_assumed": base.nu,
    })

results = pd.DataFrame(rows)

if not np.all(np.isfinite(
    results[
        ["axial_shortening_mm",
         "radial_contraction_mm",
         "superposition_error_m"]
    ].to_numpy()
)):
    raise RuntimeError("Non-finite sensitivity result.")

if results["superposition_error_m"].max() > 1e-10:
    raise RuntimeError(
        "Direct FEM and superposition results disagree."
    )

output_file = (
    OUTPUT_DIR / "fem_eigenstrain_sensitivity.csv"
)
results.to_csv(output_file, index=False)

print("\nEIGENSTRAIN ASSUMPTION SENSITIVITY")
print("-" * 68)
print(
    results.to_string(
        index=False,
        float_format=lambda x: f"{x:.9g}",
    )
)
print(
    "\nMaximum superposition error (m):",
    results["superposition_error_m"].max()
)
print("Saved:", output_file)
print(
    "\nLIMITATION: Alpha is an exploratory assumption "
    "multiplier, not a calibrated material parameter."
)