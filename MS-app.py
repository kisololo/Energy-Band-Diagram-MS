import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------
# GLOBAL PLOT STYLE
# ---------------------------------------------------------------------
plt.rcParams["font.family"] = "Arial"
plt.rcParams["figure.figsize"] = (11, 7)
plt.rcParams["axes.linewidth"] = 1.8
plt.rcParams["font.size"] = 16
plt.rcParams["lines.linewidth"] = 2.4

# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------
q = 1.602e-19
eps0 = 8.854e-12
kB = 8.617e-5  # eV/K

# ---------------------------------------------------------------------
# Material Database
# ---------------------------------------------------------------------
materials = {
    "Si": {"Eg": 1.12, "chi": 4.05, "eps": 11.7, "Nc": 2.8e19},
    "GaAs": {"Eg": 1.42, "chi": 4.07, "eps": 12.9, "Nc": 4.7e17},
    "4H-SiC": {"Eg": 3.26, "chi": 3.70, "eps": 9.7, "Nc": 1.6e19},
    "GaN": {"Eg": 3.40, "chi": 4.10, "eps": 9.5, "Nc": 2.3e18},
    "Ga2O3": {"Eg": 4.80, "chi": 4.00, "eps": 10.2, "Nc": 4.0e18},
}

# ---------------------------------------------------------------------
# Metal Database
# ---------------------------------------------------------------------
metals = {
    "Al": 4.28,
    "Ti": 4.33,
    "Mo": 4.60,
    "Au": 5.10,
    "Ni": 5.15,
    "Pt": 5.65,
    "Pd": 5.60,
}

# ---------------------------------------------------------------------
# Physics Engine (copied exactly from your code)
# ---------------------------------------------------------------------
def compute_schottky(Eg, chi, phi_m, Nd_cm3, eps_r, Nc_cm3, Vapp, T, xmin, xmax):

    Nd = Nd_cm3 * 1e6
    Nc = Nc_cm3
    eps = eps_r * eps0

    phi_Bn = phi_m - chi
    phi_bi = phi_Bn - kB * T * np.log(Nc / Nd_cm3)

    x_semi = np.linspace(0, xmax * 1e-9, 1200)
    x_m = np.linspace(xmin * 1e-9, 0, 600)

    # Collapse condition
    if phi_bi - Vapp <= 0:
        L = xmax * 1e-9
        Vx = -Vapp * (x_semi / L)
        E0 = -Vx
        E0_m = np.zeros_like(x_m)

        x_full = np.concatenate((x_m, x_semi))
        E0_vac = np.concatenate((E0_m, E0))

        Ec1 = -phi_m * np.ones_like(x_m)
        Ef1 = Ec1.copy()

        Ec2 = E0 - chi
        Ev2 = Ec2 - Eg
        Ef2 = Ec2 - kB * T * np.log(Nc / Nd_cm3)

        return x_m*1e9, x_semi*1e9, Ec1, Ef1, Ec2, Ev2, Ef2, E0, x_full*1e9, E0_vac, 0, phi_Bn, phi_bi

    # Normal Schottky
    xN = np.sqrt(2 * eps * (phi_bi - Vapp) / (q * Nd))

    Vx = np.zeros_like(x_semi)
    region2 = (x_semi <= xN)
    region3 = (x_semi >= xN)

    Vx[region2] = phi_bi - Vapp - (q * Nd / (2 * eps)) * ((xN - x_semi[region2]) ** 2)
    Vx[region3] = (q * Nd / (2 * eps)) * (xN**2)

    E0 = -Vx
    E0_m = np.zeros_like(x_m)

    x_full = np.concatenate((x_m, x_semi))
    E0_vac = np.concatenate((E0_m, E0))

    Ec1 = -phi_m * np.ones_like(x_m)
    Ef1 = Ec1.copy()

    Ec2 = E0 - chi
    Ev2 = Ec2 - Eg
    Ef_s = -(chi + phi_Bn - Vapp)
    Ef2 = Ef_s * np.ones_like(x_semi)

    return x_m*1e9, x_semi*1e9, Ec1, Ef1, Ec2, Ev2, Ef2, E0, x_full*1e9, E0_vac, xN*1e9, phi_Bn, phi_bi


# ---------------------------------------------------------------------
# STREAMLIT UI
# ---------------------------------------------------------------------
st.title("Schottky Contact Energy Band Diagram")

# ───────────────────────────────────────────
# Layout: Left parameters | Right plot
# ───────────────────────────────────────────
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Material Selection")
    mat = st.selectbox("Semiconductor Material", list(materials.keys()))
    metal = st.selectbox("Metal", list(metals.keys()))

    st.subheader("Parameters")

    Eg = st.number_input("Bandgap Eg (eV)", value=materials[mat]["Eg"])
    chi = st.number_input("Electron affinity χ (eV)", value=materials[mat]["chi"])
    eps_r = st.number_input("Dielectric constant εr", value=materials[mat]["eps"])
    Nc = st.number_input("Nc (cm⁻³)", value=float(materials[mat]["Nc"]))

    Nd_scaled = st.slider("Nd (×1e16 cm⁻³)", 0.1, 100.0, 1.0)
    Nd = Nd_scaled * 1e16

    phi_m = st.number_input("Metal work function Φm (eV)", value=metals[metal])

    Vapp = st.slider("Applied Bias Vapp (V)", -5.0, 5.0, 0.0)
    T = st.number_input("Temperature (K)", value=300.0)

    st.subheader("Plot Range")
    xmin = st.number_input("Xmin (nm)", value=-200.0)
    xmax = st.number_input("Xmax (nm)", value=1000.0)
    ymin = st.number_input("Ymin (eV)", value=-12.0)
    ymax = st.number_input("Ymax (eV)", value=1.0)

# Button
plot_button = st.button("Generate Band Diagram")

# ───────────────────────────────────────────
# PLOT
# ───────────────────────────────────────────
if plot_button:

    (x_m, x_semi, Ec1, Ef1, Ec2, Ev2, Ef2,
     E0, x_full, E0_vac, xN, phi_Bn, phi_bi) = compute_schottky(
        Eg, chi, phi_m, Nd, eps_r, Nc, Vapp, T, xmin, xmax
    )

    fig, ax = plt.subplots()

    header = (
        f"Material: {mat}   Eg={Eg:.2f} eV   χ={chi:.2f} eV   εr={eps_r:.1f}   Nc={Nc:.2e} cm⁻³\n"
        f"Metal: {metal} (Φm={phi_m:.2f} eV)   φBn={phi_Bn:.2f} eV   "
        f"φbi={phi_bi:.2f} eV   xN={xN:.1f} nm   Vapp={Vapp:.2f} V"
    )

    fig.text(
        0.5, 0.97, header,
        fontsize=16, ha="center", va="top",
        bbox=dict(facecolor=(1,1,1,0.75), edgecolor="none", pad=12)
    )

    # Metal states shading
    ax.plot(x_m, Ef1, color="#4472c4", label="Ef metal")
    ax.fill_between(x_m, Ef1+0.1, Ef1-0.1, color="#9bbad0", alpha=0.45)
    ax.fill_between(x_m, Ef1, ymin, color="#e3e9f2", alpha=0.55)

    # Vacuum
    ax.plot(x_full, E0_vac, "--", color="#9aa4b0", linewidth=1.8)

    # Semiconductor
    ax.plot(x_semi, Ec2, color="#b44e4e", label="Ec")
    ax.plot(x_semi, Ev2, color="#7d6ab0", label="Ev")
    ax.plot(x_semi, Ef2, "--", color="#6b705c", label="Ef")

    ax.axvspan(xmin, 0, color="#e8eef4", alpha=0.42)
    ax.axvline(0, color="black", linewidth=2)

    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.set_xlabel("Position (nm)", fontsize=18)
    ax.set_ylabel("Energy (eV)", fontsize=18)
    ax.legend(fontsize=14)

    st.pyplot(fig)
