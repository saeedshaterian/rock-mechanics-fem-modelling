
from pathlib import Path

import numpy as np
import pandas as pd

from skfem import (
    MeshTri,
    Basis,
    ElementTriP1,
    ElementVector,
    BilinearForm,
    LinearForm,
    asm,
    condense,
    solve,
)


# ---------------------------------------------------------
# 1. Model parameters
# ---------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

R = 0.01885
L = 0.06818

E = 11.244e9
nu = 0.191

# Independent prescribed isotropic eigenstrain.
EPS_STAR = -0.002

mu = E / (2.0 * (1.0 + nu))
lam = E * nu / ((1.0 + nu) * (1.0 - 2.0 * nu))
K_bulk = E / (3.0 * (1.0 - 2.0 * nu))

MESH_LEVELS = [(10, 20), (20, 40), (40, 80)]

rows = []


# ---------------------------------------------------------
# 2. Mesh convergence and analytical validation
# ---------------------------------------------------------

for NR, NZ in MESH_LEVELS:

    mesh = MeshTri.init_tensor(
        np.linspace(0.0, R, NR + 1),
        np.linspace(0.0, L, NZ + 1),
    )

    element = ElementVector(ElementTriP1())
    basis = Basis(mesh, element)

    @BilinearForm
    def elasticity(u, v, w):
        err_u = u.grad[0, 0]
        ezz_u = u.grad[1, 1]
        ett_u = u[0] / w.x[0]
        erz_u = 0.5 * (
            u.grad[0, 1] + u.grad[1, 0]
        )

        err_v = v.grad[0, 0]
        ezz_v = v.grad[1, 1]
        ett_v = v[0] / w.x[0]
        erz_v = 0.5 * (
            v.grad[0, 1] + v.grad[1, 0]
        )

        div_u = err_u + ezz_u + ett_u
        div_v = err_v + ezz_v + ett_v

        strain_product = (
            err_u * err_v
            + ezz_u * ezz_v
            + ett_u * ett_v
            + 2.0 * erz_u * erz_v
        )

        return (
            lam * div_u * div_v
            + 2.0 * mu * strain_product
        ) * w.x[0]

    @LinearForm
    def eigenstrain_load(v, w):
        div_v = (
            v.grad[0, 0]
            + v.grad[1, 1]
            + v[0] / w.x[0]
        )

        return (
            3.0 * K_bulk * EPS_STAR
            * div_v * w.x[0]
        )

    K = asm(elasticity, basis)
    f = asm(eigenstrain_load, basis)

    axis_facets = mesh.facets_satisfying(
        lambda x: np.isclose(x[0], 0.0)
    )

    radial_axis_dofs = basis.get_dofs(
        facets=axis_facets
    ).all(["u^1"])

        # Anchor axial displacement at the bottom-axis node.
    coordinates = mesh.p

    bottom_axis_node = np.flatnonzero(
        np.isclose(coordinates[0], 0.0)
        & np.isclose(coordinates[1], 0.0)
    )

    if len(bottom_axis_node) != 1:
        raise RuntimeError(
            "Expected exactly one bottom-axis node."
        )

    bottom_axis_dofs = np.array([
        basis.nodal_dofs[1, bottom_axis_node[0]]
    ], dtype=int)

    D = np.unique(
        np.concatenate([
            radial_axis_dofs,
            bottom_axis_dofs,
        ])
    )
    D = np.unique(
        np.concatenate([
            radial_axis_dofs,
            bottom_axis_dofs,
        ])
    )

    # Solve the constrained FEM system.
    u = solve(*condense(K, f, D=D))

    if not np.all(np.isfinite(u)):
        raise RuntimeError(
            "FEM solution contains non-finite values."
        )

    # Analytical displacement field:
    # ur = EPS_STAR * r
    # uz = EPS_STAR * z
    # Analytical displacement field:
    # ur = EPS_STAR * r
    # uz = EPS_STAR * z

    coordinates = basis.doflocs

    radial_dofs = basis.get_dofs().all(["u^1"])
    axial_dofs = basis.get_dofs().all(["u^2"])

    # Compare all vector DOFs using their component labels.
    all_radial_dofs = np.arange(0, basis.N, 2)
    all_axial_dofs = np.arange(1, basis.N, 2)

    u_exact = np.zeros(basis.N)
    u_exact[all_radial_dofs] = (
        EPS_STAR * coordinates[0, all_radial_dofs]
    )
    u_exact[all_axial_dofs] = (
        EPS_STAR * coordinates[1, all_axial_dofs]
    )

    error = u - u_exact

    max_abs_error = float(np.max(np.abs(error)))
    reference_displacement = abs(EPS_STAR) * L

    relative_error = (
        max_abs_error / reference_displacement
    )

    # Mechanical residual of the analytical solution.
    residual = K @ u_exact - f

    free_dofs = np.setdiff1d(
        np.arange(basis.N), D
    )

    relative_equilibrium_residual = (
        np.linalg.norm(residual[free_dofs])
        / max(np.linalg.norm(f[free_dofs]), 1e-30)
    )


    # -----------------------------------------------------
    # Direct numerical stress validation at quadrature points
    # -----------------------------------------------------

    uh = basis.interpolate(u)

    err = uh.grad[0, 0]
    ezz = uh.grad[1, 1]
    erz = 0.5 * (uh.grad[0, 1] + uh.grad[1, 0])

    # Axisymmetric hoop strain: u_r / r
    radial_coordinates = basis.global_coordinates()[0]
    ett = uh.value[0] / radial_coordinates

    # Mechanical strains after subtracting eigenstrain
    mechanical_rr = err - EPS_STAR
    mechanical_zz = ezz - EPS_STAR
    mechanical_tt = ett - EPS_STAR

    mechanical_trace = (
        mechanical_rr + mechanical_zz + mechanical_tt
    )

    sigma_rr = (
        lam * mechanical_trace + 2.0 * mu * mechanical_rr
    )
    sigma_zz = (
        lam * mechanical_trace + 2.0 * mu * mechanical_zz
    )
    sigma_tt = (
        lam * mechanical_trace + 2.0 * mu * mechanical_tt
    )
    sigma_rz = 2.0 * mu * erz

    max_stress_pa = float(max(
        np.max(np.abs(sigma_rr)),
        np.max(np.abs(sigma_zz)),
        np.max(np.abs(sigma_tt)),
        np.max(np.abs(sigma_rz)),
    ))

    stress_scale_pa = E * abs(EPS_STAR)
    relative_stress_error = max_stress_pa / stress_scale_pa

    rows.append({
        "NR": NR,
        "NZ": NZ,
        "number_of_elements": mesh.nelements,
        "number_of_dofs": basis.N,
        "eigenstrain": EPS_STAR,
        "max_displacement_error_m": max_abs_error,
        "relative_displacement_error": relative_error,
        "relative_equilibrium_residual": relative_equilibrium_residual,
        "max_stress_pa": max_stress_pa,
        "relative_stress_error": relative_stress_error,
    })
# ---------------------------------------------------------
# 3. Save results
# ---------------------------------------------------------

results = pd.DataFrame(rows)

output_file = (
    OUTPUT_DIR / "fem_eigenstrain_validation.csv"
)

results.to_csv(output_file, index=False)

print("\nEIGENSTRAIN VALIDATION RESULTS")
print("-" * 72)
print(results.to_string(index=False))

print("\nAnalytical solution:")
print("ur = eigenstrain * r")
print("uz = eigenstrain * z")
print("Mechanical stress = 0")

print(f"\nResults saved to: {output_file}")
print("\nDOF DIAGNOSTICS")
print("-" * 60)

print("First 12 DOF coordinates:")
print(basis.doflocs[:, :12])

print("\nFirst 12 numerical displacements:")
print(u[:12])

print("\nFirst 12 analytical displacements:")
print(u_exact[:12])

print("\nConstrained DOFs:")
print(D[:20])

print("\nNumerical displacement at constrained DOFs:")
print(u[D[:20]])

print("\nAnalytical displacement at constrained DOFs:")
print(u_exact[D[:20]])

print("\nMaximum difference at constrained DOFs:")
print(np.max(np.abs(u[D] - u_exact[D])))

print("\nMaximum difference at free DOFs:")
print(np.max(np.abs(u[free_dofs] - u_exact[free_dofs])))
