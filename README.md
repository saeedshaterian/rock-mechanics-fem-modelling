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
