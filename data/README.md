# Experimental Data

## Dataset

File: experimental_data.csv

Sample: B9
Number of observations: 72

The dataset contains experimental petrophysical measurements
under different pressure-loading and recovery conditions.

## Variables

- sample: Rock sample identifier
- pressure_psi: Measurement pressure (psi)
- porosity_pct: Porosity (%)
- permeability_mD: Permeability (mD)
- pore_volume_cc: Source-data field; physical interpretation and units require verification
- stage: Loading or recovery stage
- rest_time_hr: Recovery duration (hours)

## Experimental Stages

- initial_loading: 8 observations
- 5000psi_loading: 8 observations
- 7000psi_loading: 8 observations
- rest_after_5000psi: 24 observations
- rest_after_7000psi: 24 observations

## Important Notes

Porosity and permeability are experimental measurements.

The finite element displacement results are model predictions,
not experimentally measured rock deformation.

Elastic parameters used in the FEM simulations are illustrative
and are not calibrated to sample B9.

The original experimental source, reuse permissions, and
interpretation of the pore_volume_cc field should be verified
before public distribution.
