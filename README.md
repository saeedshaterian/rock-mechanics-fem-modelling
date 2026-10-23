# History-Dependent Rock Deformation
## Axisymmetric Finite Element Modelling and Validation

### Overview

This repository presents a Python-based finite element modelling
workflow for investigating pressure-dependent and history-dependent
deformation of carbonate reservoir rocks.

The project combines:

- Axisymmetric linear-elastic finite element analysis
- Analytical benchmark validation
- Mesh convergence assessment
- Pressure-dependent deformation modelling
- Loading-history eigenstrain representation
- Pressure-history and recovery analysis
- Elastic parameter sensitivity analysis

### Experimental Data

The petrophysical dataset contains 72 observations from carbonate
rock sample B9, including porosity and permeability measurements
across loading and recovery stages.

### Numerical Framework

The numerical implementation uses Python and scikit-fem.

The reference model assumes:

- Axisymmetric cylindrical geometry
- Homogeneous isotropic linear elasticity
- Illustrative Young's modulus: 11.244 GPa
- Illustrative Poisson's ratio: 0.191
- Pressure-dependent boundary loading

History-dependent eigenstrains are inferred from observed porosity
changes under a constant-grain-volume assumption.

### Verification

The elastic FEM implementation was compared against analytical
solutions at pressures of 800, 3600 and 5700 psi.

Mesh convergence was evaluated using 400, 1600, 6400 and 25600
elements.

The homogeneous linear-elastic benchmark showed agreement with
analytical displacement solutions to numerical precision.

### Main Results

At 5700 psi, the reference elastic model predicts:

- Axial shortening: approximately 0.147271 mm
- Radial contraction: approximately 0.040717 mm

For the combined 7000-psi loading-history scenario, the model
predicts approximately:

- Axial shortening: 0.434116 mm
- Radial contraction: 0.120022 mm

A sensitivity analysis was performed across 25 combinations of
assumed Young's modulus and Poisson's ratio.

### Scientific Limitations

The elastic parameters are illustrative and have not been calibrated
to sample B9.

History eigenstrains are inferred from porosity measurements rather
than independently measured mechanical strains.

Predicted displacements are numerical estimates, not experimentally
validated deformation measurements.

Analytical benchmark agreement verifies the linear-elastic
implementation but does not independently validate the
history-dependent constitutive assumptions.

### Requirements

Install dependencies using:

    pip install -r requirements.txt

### Reproducibility

Example commands:

    python analysis/fem_independent_validation.py
    python analysis/fem_mesh_convergence.py
    python analysis/fem_history_fem.py
    python analysis/fem_parameter_sensitivity.py

### Research Applications

- Computational rock mechanics
- Subsurface geomechanics
- Pressure-induced deformation
- Finite element modelling
- History-dependent rock behaviour

### Model Geometry and Boundary Conditions

The reference numerical model represents an axisymmetric
cylindrical specimen with:

- Radius: 0.01885 m
- Length: 0.06818 m

The elastic benchmark considers homogeneous isotropic
linear elasticity under prescribed pressure loading.

Axisymmetric displacement constraints and axial reference
constraints are applied according to the individual scripts.

The axial benchmark uses a separate uniaxial loading
configuration.

### Output Files

The figures directory contains numerical results including:

- Elastic benchmark comparisons
- Independent FEM verification results
- Mesh convergence results
- Pressure sweep predictions
- Loading-history deformation estimates
- Recovery-stage predictions
- Elastic parameter sensitivity results

CSV files provide numerical outputs, while PNG files
visualize selected sensitivity results.

### Verification Versus Experimental Validation

Analytical comparisons and mesh studies assess the
numerical implementation of the linear-elastic problem.

They do not establish experimental validation of the
history-dependent model.

Independent mechanical deformation measurements and
sample-specific elastic calibration would be required
for stronger experimental validation.

### FEM Recovery-Model and Temporal Sensitivity Comparisons

Two scripts examine how alternative porosity-evolution inputs affect
axisymmetric FEM deformation estimates:

- `analysis/compare_fem_recovery_inputs.py`
- `analysis/compare_fem_temporal_inputs.py`

The recovery-input analysis and temporal-input analysis are separate
workflows, and their numerical outputs should not be conflated.

#### Temporal Model Comparison

The temporal analysis compares five models:

- `stage_only`
- `stage_plus_time`
- `time_only`
- `anchored_time`
- `hybrid_recovery_model`

Each model is evaluated for 64 scenarios, giving 320 detailed FEM
output rows.

The outputs are:

- `figures/fem_temporal_inputs_detailed.csv` (320 rows)
- `figures/fem_temporal_inputs_summary.csv` (40 rows)
- `figures/fem_temporal_inputs_comparison.csv` (8 aggregated rows)

The `time_only` model uses pressure-specific reference porosity and
a pressure-independent logarithmic time coefficient.

#### Recovery-Input Comparison

The separate recovery-input analysis is implemented in
`analysis/compare_fem_recovery_inputs.py`.

Its existing outputs include:

- `figures/fem_recovery_inputs_comparison.csv`
- `figures/fem_recovery_inputs_summary.csv`

#### Interpretation and Limitations

These analyses assess the sensitivity of predicted deformation to
the selected porosity-evolution formulation.

The forecasts are model-dependent scenarios, not independently
validated displacement predictions. Sample-specific elastic
calibration and independent mechanical strain measurements would
be needed for stronger experimental validation.


### Numerical Verification and Boundary-Condition Assessment

The finite element implementation was subjected to additional numerical verification and a systematic review of its boundary-condition definitions.

#### Boundary Conditions

For the axisymmetric pressure-loading and history-dependent models:

- Radial displacement is constrained along the symmetry axis (`r = 0`).
- A single axial displacement degree of freedom is constrained at the bottom-axis node (`r = 0, z = 0`) to remove rigid-body axial translation.
- The bottom-axis node is identified directly from mesh coordinates, with an explicit check that exactly one node is selected.

The independent validation script uses the same direct nodal degree-of-freedom approach.

The separate uniaxial benchmark constrains axial displacement along the entire bottom face. This is consistent with its analytical reference solution for uniform axial compression and traction-free lateral surfaces.

#### Analytical and Numerical Verification

The homogeneous elastic cylinder was evaluated against analytical displacement solutions under prescribed pressure loading.

The reference pressure-loading benchmark at 5700 psi gives approximately:

- Analytical and FEM axial shortening: 0.147271 mm
- Analytical and FEM radial contraction: 0.040717 mm

Mesh convergence was assessed across four mesh resolutions and three pressure levels.

An additional uniform-eigenstrain verification test was implemented in `analysis/fem_eigenstrain_validation.py`.

For a prescribed uniform isotropic eigenstrain, the numerical displacement field was compared with the corresponding stress-free analytical solution.

Across the tested meshes, the maximum absolute displacement discrepancy was approximately `2.76e-15 m`. The maximum computed mechanical stress was approximately `0.023842 Pa`, corresponding to a relative stress scale of approximately `1.06e-9` for the finest mesh.

These results support the numerical consistency of the implemented eigenstrain formulation for the homogeneous benchmark.

#### Boundary-Condition Revision and Regression Checks

The axial reference constraint was made explicit in the relevant pressure-loading, history-dependent, recovery-comparison, and temporal-comparison scripts.

Previously generated CSV outputs were retained as local backups and compared with the results obtained after the boundary-condition revision.

For the directly compared outputs:

- Input pressure, porosity, permeability, and eigenstrain quantities remained unchanged.
- Differences in FEM axial displacements were on the order of `1e-14` to `1e-12 mm`, depending on the analysis.
- Differences in FEM radial displacements were on the order of `1e-15` to `1e-14 mm`.
- No materially significant change in the reported deformation results was observed.

The regression checks establish consistency of the numerical outputs following the boundary-condition revision. They do not constitute independent experimental validation.

#### Scope and Limitations

Analytical displacement agreement, mesh refinement, eigenstrain verification, and regression comparisons provide evidence for the numerical implementation of the tested problems.

The history-dependent deformation formulation remains exploratory. Its eigenstrains are inferred from porosity changes under a constant-grain-volume assumption, and its elastic parameters are illustrative rather than calibrated to sample B9.

Consequently, the predicted history-dependent displacements should not be interpreted as independently validated mechanical deformation measurements.

### Optimized Exponential Porosity Evolution and FEM Sensitivity

An additional analysis investigates post-loading porosity evolution for carbonate sample B9 following the 7000-psi loading-history stage.

The model uses the measured porosity at 96 hours as a pressure-specific reference:

\[
\phi(P,t)=\phi(P,96)+(A+Bz)\left[1-\exp\left(-\frac{t-96}{\tau}\right)\right]
\]

where \(z=(P-800)/4900\), pressure is expressed in psi, and time is expressed in hours.

The optimized parameters are:

- Characteristic time \(\tau=133.29506125\) hours
- Coefficient \(A=-0.12721701\) porosity percentage points
- Coefficient \(B=0.13018682\) porosity percentage points
- In-sample porosity RMSE: 0.00556241 percentage points

The model was fitted using observations at 197 and 730 hours, with measured 96-hour porosity values defining the reference state.

The corresponding FEM sensitivity analysis includes 24 pressure–time scenarios covering eight pressure levels and three observation times.

The analysis is implemented in:

- `analysis/compare_fem_exponential_optimized.py`

Results are saved to:

- `figures/fem_exponential_optimized_comparison.csv`

The porosity-based eigenstrain is evaluated under a constant-grain-volume assumption and propagated through the axisymmetric linear-elastic FEM formulation.

The optimized exponential model is calibrated to the available observations. Its in-sample reconstruction accuracy does not establish independent temporal predictive validity.

The resulting FEM displacements are model-dependent numerical estimates and have not been independently validated against measured mechanical deformation.
