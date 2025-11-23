import streamlit as st
import numpy as np
import matplotlib.pyplot as plt


st.set_page_config(
    page_title="Schottky Band Diagram",
    page_icon="⚡",
)

# ------------------------------
# Google Analytics (GA4)
# ------------------------------
# st.markdown("""
# <!-- Google tag (gtag.js) -->
# <script async src="https://www.googletagmanager.com/gtag/js?id=G-7SJTF762GX"></script>
# <script>
#   window.dataLayer = window.dataLayer || [];
#   function gtag(){dataLayer.push(arguments);}
#   gtag('js', new Date());
#   gtag('config', 'G-7SJTF762GX');
# </script>
# """, unsafe_allow_html=True)


# ---------------------------------------------------------------------
# GLOBAL PLOT STYLE
# ---------------------------------------------------------------------
plt.rcParams["font.family"] = "Arial"
plt.rcParams["figure.figsize"] = (8, 5)
plt.rcParams["axes.linewidth"] = 1.8
plt.rcParams["font.size"] = 12
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
# Physics Engine
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
# STREAMLIT UI — with TABS + FIXED Vapp Sync
# ---------------------------------------------------------------------
st.set_page_config(layout="wide")
# st.title("Schottky Contact Energy Band Diagram")
st.markdown("""
    <style>
        .block-container { padding-top: 1.2rem; }
    </style>
""", unsafe_allow_html=True)

st.markdown(
    "<h1 style='font-size:32px; font-weight:600; font-family:Arial;'>"
    "Schottky Contact Energy Band Diagram"
    "</h1>",
    unsafe_allow_html=True
)


left, right = st.columns([1.04, 2])

#  Initialize session state for Vapp
if "Vapp" not in st.session_state:
    st.session_state["Vapp"] = 0.0

if "Vapp_slider" not in st.session_state:
    st.session_state["Vapp_slider"] = 0.0

# Sync functions
def sync_from_box():
    st.session_state["Vapp_slider"] = st.session_state["Vapp"]

def sync_from_slider():
    st.session_state["Vapp"] = st.session_state["Vapp_slider"]


# ==============================
# LEFT PANEL (TABS)
# ==============================
with left:
    tabs = st.tabs(["Material", "Semiconductor", "Metal", "Bias", "Plot Range", "Notes"])

    # ---- Tab 1: Material ----
    with tabs[0]:
        mat = st.selectbox("Semiconductor Material", list(materials.keys()), index=list(materials.keys()).index("Ga2O3"))
        metal = st.selectbox("Metal", list(metals.keys()), index=list(metals.keys()).index("Ni"))

    # ---- Tab 2: Semiconductor ----
    with tabs[1]:
        Eg = st.number_input("Bandgap Eg (eV)", value=materials[mat]["Eg"])
        chi = st.number_input("Electron affinity χ (eV)", value=materials[mat]["chi"])
        eps_r = st.number_input("Dielectric constant εr", value=materials[mat]["eps"])
        Nc = st.number_input(
            "Nc (cm⁻³)",
            value=float(materials[mat]["Nc"]),
            format="%.2e"
        )
        Nd_scaled = st.slider("Nd (×1e16 cm⁻³)", 0.1, 100.0, 1.0)
        Nd = Nd_scaled * 1e16

    # ---- Tab 3: Metal ----
    with tabs[2]:
        phi_m = st.number_input("Metal work function Φm (eV)", value=metals[metal])

    # ---- Tab 4: Bias (Synced Inputs)----
    with tabs[3]:
        st.number_input(
            "Enter Vapp (V)",
            key="Vapp",
            on_change=sync_from_box
        )

        st.slider(
            "Adjust Vapp",
            -5.0,
            5.0,
            key="Vapp_slider",
            on_change=sync_from_slider
        )

        Vapp = st.session_state["Vapp"]

        T = st.number_input("Temperature (K)", value=300.0)

    # ---- Tab 5: Plot Range ----
    with tabs[4]:
        xmin = st.number_input("Xmin (nm)", value=-200.0)
        xmax = st.number_input("Xmax (nm)", value=1000.0)
        ymin = st.number_input("Ymin (eV)", value=-12.0)
        ymax = st.number_input("Ymax (eV)", value=1.0)

    # ---- Tab 6: Notes ----
    with tabs[5]:
        st.markdown(
            """
            <p style='font-family:Arial; font-size:14px; line-height:1.2;'>
            <b>Model Notes</b>
            </p>
            <p style='font-family:Arial; font-size:12px; line-height:1.2;'>
            This simulator is for a clean, classical Schottky contact model.
            The following physical effects are <b>included</b>:
            </p>
    
            <ul style='font-family:Arial; font-size:12px; line-height:1.2;'>
                <li>1D band diagram under depletion approximation</li>
                <li>Classical electrostatics (Poisson equation)</li>                
            </ul>
    
            <p style='font-family:Arial; font-size:12px; line-height:1.2;'>
            The following important physics are <b>not yet included</b> in this version:
            </p>
    
            <ul style='font-family:Arial; font-size:12px; line-height:1.2;'>
                <li>Image-force barrier lowering</li>
                <li>Fermi-level pinning</li>
                <li>Deep levels / traps / interface states</li>
                <li>Temperature-dependent:
                    <ul>
                        <li>E<sub>g</sub>(T) bandgap narrowing</li>
                        <li>N<sub>c</sub>, N<sub>v</sub> density-of-states scaling</li>
                    </ul>
                </li>
                <li>Non-uniform doping</li>
            </ul>
    
            <p style='font-family:Arial; font-size:12px;'>
            These features may appear in future versions of the simulator.
            For research-grade analysis, please interpret results with these limitations in mind.
            </p>
            """,
            unsafe_allow_html=True
        )

# ==============================
# RIGHT PANEL — PLOT (Auto-updates)
# ==============================
with right:

    (x_m, x_semi, Ec1, Ef1, Ec2, Ev2, Ef2,
     E0, x_full, E0_vac, xN, phi_Bn, phi_bi) = compute_schottky(
        Eg, chi, phi_m, Nd, eps_r, Nc, Vapp, T, xmin, xmax
    )

    fig, ax = plt.subplots()

    # --- Clean inline labels above the plot (no box) ---
    # --- Clean labels ABOVE the plot using fig.text (outside axes) ---
    # --- Clean, math-mode labels above the plot ---
    fig.text(
        0.5, 0.985,
        (
            f"Material: {mat}   "
            rf"$E_g={Eg:.2f}\,$eV   "
            rf"$\chi={chi:.2f}\,$eV   "
            rf"$\varepsilon_r={eps_r:.1f}$   "
            rf"$N_c={Nc:.2e}\,\mathrm{{cm}}^{{-3}}$"
        ),
        ha="center", va="top", fontsize=11, fontfamily="Arial"
    )

    fig.text(
        0.5, 0.945,
        (
            f"Metal: {metal}   "
            rf"$\Phi_m={phi_m:.2f}\,$eV   "
            rf"$\phi_{{Bn}}={phi_Bn:.2f}\,$eV   "
            rf"$\phi_{{bi}}={phi_bi:.2f}\,$eV   "
            rf"$x_N={xN:.1f}\,$nm   "
            rf"$V_{{app}}={Vapp:.2f}\,$V"
        ),
        ha="center", va="top", fontsize=11, fontfamily="Arial"
    )

    # Vacuum level
    ax.plot(x_full, E0_vac, "--", color="#9aa4b0", linewidth=1.8, label=r"$E_0$ (vacuum)")

    # Metal
    ax.plot(x_m, Ef1, color="#FFC000", label=r"$E_F$ metal")
    ax.fill_between(x_m, Ef1 - 0.1, Ef1 + 0.1, color="#FFD966", alpha=0.45)
    # ax.fill_between(x_m, Ef1, Ef1 - 8, color="#FFD966", alpha=1)
    ax.fill_between(x_m, Ef1, ymin, color="#e3e9f2", alpha=0.55)



    # Semiconductor
    ax.plot(x_semi, Ec2, color="#b44e4e", label=r"$E_C$")
    ax.plot(x_semi, Ev2, color="#7d6ab0", label=r"$E_V$")
    ax.plot(x_semi, Ef2, "--", color="#6b705c", label=r"$E_{Fn}$")

    ax.axvspan(xmin, 0, color="#e8eef4", alpha=0.42)
    ax.axvline(0, color="black", linewidth=2)

    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.set_xlabel("Position (nm)", fontsize=14)
    ax.set_ylabel("Energy (eV)", fontsize=14)
    ax.legend(fontsize=10, loc="upper right", frameon=True)

    st.pyplot(fig)


footer = """
<style>
.footerbox {
    width: 100%;
    margin-top: 5px;
    padding: 25px 0;
    text-align: center;
    color: #bbbbbb;
    font-size: 15px;
    line-height: 1.5;
    border-top: 1px solid #444444;
}
.footerbox a {
    color: #bbbbbb !important;
    text-decoration: underline;
}
</style>

<div class="footerbox">
<b>Schottky Contact Energy Band Diagram Simulator</b><br>
Developed by Kai Fu, University of Utah<br>
Version 1.0 (2025)<br>

<!-- CUSTOM SPACING ABOVE GITHUB LINK -->
<div style="margin: 20px 0;"></div>

<a href="https://github.com/kisololo/Energy-Band-Diagram-MS" target="_blank">
GitHub Repository (Source Code)
</a>

<!-- CUSTOM SPACING BELOW GITHUB LINK -->
<div style="margin: 20px 0;"></div>

Citation:<br>
If you use this app for teaching or research, please cite:<br>
<i>Kai Fu, "Interactive Schottky Contact Energy Band Diagram Simulator," 2025.</i>
</div>

"""
st.markdown(footer, unsafe_allow_html=True)




