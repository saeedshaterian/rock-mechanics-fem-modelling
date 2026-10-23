from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "experimental_data.csv"
FEM_FILE = ROOT / "figures" / "fem_temporal_inputs_detailed.csv"
OUTPUT_FILE = ROOT / "figures" / "fem_exponential_recovery_comparison.csv"

STAGE = "rest_after_7000psi"
TAU_HR = 120.0

# Rounded coefficients from the joint fit at tau = 120 h.
A = -0.124753
B = 0.127549

data = pd.read_csv(DATA_FILE)
data = data.loc[
    data["sample"].eq("B9")
    & data["stage"].eq(STAGE)
].copy()

wide = data.pivot(
    index="pressure_psi",
    columns="rest_time_hr",
    values="porosity_pct"
).sort_index()

required_times = {96, 197, 730}
if not required_times.issubset(set(wide.columns)):
    raise ValueError("Missing required experimental times.")

fem = pd.read_csv(FEM_FILE)

required_columns = {
    "model", "stage", "pressure_psi", "rest_time_hr",
    "porosity_initial_pct", "porosity_predicted_pct",
    "eps_star_proxy",
    "pressure_only_axial_mm", "pressure_only_radial_mm",
    "history_only_axial_mm", "history_only_radial_mm",
    "combined_axial_mm", "combined_radial_mm",
    "young_modulus_GPa_assumed", "poisson_ratio_assumed",
    "mesh_elements",
}

missing = required_columns - set(fem.columns)
if missing:
    raise ValueError(f"Missing FEM columns: {sorted(missing)}")

# Use the existing stage_only FEM results as a mechanical reference.
ref = fem.loc[
    fem["model"].eq("stage_only")
    & fem["stage"].eq(STAGE)
    & fem["rest_time_hr"].isin(required_times)
].copy()

ref = ref.sort_values(
    ["rest_time_hr", "pressure_psi"]
).reset_index(drop=True)

if len(ref) != 24:
    raise ValueError(f"Expected 24 reference rows, found {len(ref)}.")

if ref.duplicated(["pressure_psi", "rest_time_hr"]).any():
    raise ValueError("Duplicate FEM scenarios.")

for col in [
    "young_modulus_GPa_assumed",
    "poisson_ratio_assumed",
    "mesh_elements",
]:
    if ref[col].nunique() != 1:
        raise ValueError(f"Inconsistent FEM setting: {col}")

ref["phi96"] = ref["pressure_psi"].map(wide[96].to_dict())

if ref["phi96"].isna().any():
    raise ValueError("Missing pressure-matched 96 h porosity.")

# Exponential recovery model.
z = (ref["pressure_psi"].to_numpy() - 800.0) / 4900.0
t = ref["rest_time_hr"].to_numpy(dtype=float)

amplitude = A + B * z
factor = -np.expm1(-(t - 96.0) / TAU_HR)

ref["exponential_porosity_pct"] = (
    ref["phi96"].to_numpy() + amplitude * factor
)

# Same porosity-to-eigenstrain proxy as the original FEM script.
phi_initial = ref["porosity_initial_pct"].to_numpy() / 100.0
phi_exponential = ref["exponential_porosity_pct"].to_numpy() / 100.0

eps_exponential = (
    np.log((1.0 - phi_initial) / (1.0 - phi_exponential))
    / 3.0
)

eps_reference = ref["eps_star_proxy"].to_numpy()

if np.any(np.abs(eps_reference) < 1e-12):
    raise ValueError("Reference eigenstrain is too close to zero.")

# Recover linear FEM displacement response per unit eigenstrain.
axial_unit = (
    ref["history_only_axial_mm"].to_numpy()
    / eps_reference
)

radial_unit = (
    ref["history_only_radial_mm"].to_numpy()
    / eps_reference
)

# Verify that the mechanical response is scenario-independent.
for name, values in [
    ("axial", axial_unit),
    ("radial", radial_unit),
]:
    if not np.allclose(values, values[0], rtol=1e-7, atol=1e-9):
        raise ValueError(
            f"Inconsistent {name} response per unit eigenstrain."
        )

ref["exponential_axial_mm"] = (
    ref["pressure_only_axial_mm"].to_numpy()
    + axial_unit * eps_exponential
)

ref["exponential_radial_mm"] = (
    ref["pressure_only_radial_mm"].to_numpy()
    + radial_unit * eps_exponential
)

# Compare with the existing stage_only model.
ref["delta_porosity_pp"] = (
    ref["exponential_porosity_pct"]
    - ref["porosity_predicted_pct"]
)

ref["delta_axial_mm"] = (
    ref["exponential_axial_mm"]
    - ref["combined_axial_mm"]
)

ref["delta_radial_mm"] = (
    ref["exponential_radial_mm"]
    - ref["combined_radial_mm"]
)

# Experimental porosity reconstruction error.
observed = data[
    ["pressure_psi", "rest_time_hr", "porosity_pct"]
].rename(columns={"porosity_pct": "observed_porosity_pct"})

ref = ref.merge(
    observed,
    on=["pressure_psi", "rest_time_hr"],
    how="left",
    validate="one_to_one"
)

if ref["observed_porosity_pct"].isna().any():
    raise ValueError("Missing observed porosity values.")

ref["porosity_error_pp"] = (
    ref["exponential_porosity_pct"]
    - ref["observed_porosity_pct"]
)

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
ref.to_csv(OUTPUT_FILE, index=False)

print("\nEXPONENTIAL RECOVERY FEM SENSITIVITY")
print("=" * 65)
print("Stage:", STAGE)
print("Tau:", TAU_HR, "hours")
print("Scenarios:", len(ref))
print("Mesh elements:", ref["mesh_elements"].iloc[0])

print("\nPOROSITY RECONSTRUCTION")
for time, group in ref.groupby("rest_time_hr"):
    err = group["porosity_error_pp"].to_numpy()
    print(
        f"{time:.0f} h | "
        f"RMSE={np.sqrt(np.mean(err**2)):.6f} pp | "
        f"MAE={np.mean(np.abs(err)):.6f} pp"
    )

print("\nFEM DIFFERENCES RELATIVE TO STAGE_ONLY")
print(
    ref.groupby("rest_time_hr")[
        ["delta_porosity_pp", "delta_axial_mm", "delta_radial_mm"]
    ].agg(["mean", "min", "max"]).to_string()
)

print("\nUNIT EIGENSTRAIN RESPONSES")
print(f"Axial:  {axial_unit[0]:.8f} mm/strain")
print(f"Radial: {radial_unit[0]:.8f} mm/strain")

print("\nSaved:", OUTPUT_FILE)
print(
    "\nLIMITATIONS: In-sample calibrated recovery model; "
    "illustrative elastic parameters; no independent "
    "displacement validation."
)
