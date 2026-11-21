import pandas as pd
import streamlit as st

from utilidades.graficos import crear_figura_pareto
from modelo import calcular_k0, evaluar_hds
from optimizacion import calcular_malla_y_pareto
from sensibilidad import calcular_sensibilidad

st.set_page_config(
    page_title="Simulación y Optimización de HDS",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": "https://docs.streamlit.io",
        "Report a bug": None,
        "About": "Sección interna de simulación, versión 1.0",
    },
)

col_logo, col_titulo = st.columns([1, 8], vertical_alignment="center")
with col_logo:
    st.image(
        "https://img.magnific.com/premium-photo/nuclear-power-plant-with-nuclear-reactor-illuminated-by-lights-middle-night_124507-45320.jpg?semt=ais_hybrid&w=740&q=80",
        width=90,
    )
with col_titulo:
    st.title("Simulación y Optimización de Hidrodesulfuración (HDS)")
    st.caption(
        " Evaluación de conversión de azufre ($X_{s}$) y carga térmica del horno ($Q_{horno}$) "
        " bajo restricción de Azufre en la salida($S_{out}$) ≤ 10 ppm."
    )

with st.sidebar:
    st.header("Variables de decisión")
    t_in = st.slider("Temperatura entrada reactor $T_{in}$(K)", 550.0, 650.0, 600.0, 1.0)
    epsilon = st.slider("Efectividad intercambiador ε", 0.60, 0.90, 0.75, 0.01)

    st.header("Parámetros del modelo")
    m_dot = st.number_input("Flujo másico $ṁ$ ($kg/h$)", 90000.0, 110000.0, 100000.0, 1000.0)
    s_in = st.number_input("Azufre alimentación $S_{in}$ ($ppm$)", 450.0, 550.0, 500.0, 5.0)
    cp = st.number_input("Capacidad calorífica $Cp_{}$ ($kJ/(kg·K)$)", 2.25, 2.75, 2.50, 0.05)
    ea = st.number_input("Energía de activación $Ea$ ($J/mol$)", 72000.0, 88000.0, 80000.0, 500.0)
    tau = st.number_input("Tiempo espacial τ ($h$)", 0.45, 0.55, 0.50, 0.01)

    k0_base = calcular_k0(ea=ea, tau=tau)
    k0 = st.number_input(
        "Factor preexponencial $k_{o}$ ($h⁻¹$)",
        min_value=float(k0_base * 0.90),
        max_value=float(k0_base * 1.10),
        value=float(k0_base),
        format="%.4e",
    )

res_actual = evaluar_hds(t_in, epsilon, m_dot, s_in, cp, ea, k0, tau)

st.subheader("Punto operativo seleccionado")
if res_actual["factible"]:
    st.success(
        f"Cumple especificación de calidad: $S_{{out}}$  = {res_actual['Sout_ppm']:.2f} ppm (≤ 10 ppm).",
        icon="✅",
    )
else:
    st.warning(
        f"No cumple especificación de calidad: $S_{{out}}$  = {res_actual['Sout_ppm']:.2f} ppm (> 10 ppm).",
        icon="⚠️",
    )

c1, c2, c3, c4 = st.columns(4)
c1.metric("Conversión $X_{s}$", f"{res_actual['Xs']*100:.2f}%")
c2.metric("Azufre salida $S_{out}$", f"{res_actual['Sout_ppm']:.2f} ppm", delta_color="inverse")
c3.metric("Carga horno $Q_{horno}$", f"{res_actual['Q_horno_kW']:.2f} kW")
c4.metric("Carga horno $Q_{horno}$", f"{res_actual['Q_horno_kJ_h']:,.0f} kJ/h")

st.markdown("---")

malla_cached = st.cache_data(calcular_malla_y_pareto)
sens_cached = st.cache_data(calcular_sensibilidad)

df_grid, df_pareto, knee_point = malla_cached(
    m_dot=m_dot, s_in=s_in, cp=cp, ea=ea, k0=k0, tau=tau
)

tab_pareto, tab_sanity, tab_sensibilidad = st.tabs(
    ["Frontera de Pareto", "Sanity Checks y Malla", "Sensibilidad"]
)

with tab_pareto:
    if df_pareto.empty:
        st.error("No se encontraron puntos factibles en el dominio especificado.")
    else:
        col_graph, col_knee = st.columns([2.5, 1])

        with col_graph:
            fig = crear_figura_pareto(df_grid, df_pareto, knee_point)
            st.plotly_chart(fig, use_container_width=True)

        with col_knee:
            st.markdown("### Knee Point")
            st.info("Punto de equilibrio ideal: la mejor conversión posible con el menor consumo de energía.")
            st.metric(
                "Temperatura $T_{in}$",
                f"{knee_point['Tin_K']:.1f} K",
                f"{knee_point['Tin_K']-273.15:.1f} °C",
            )
            st.metric("Efectividad ε", f"{knee_point['epsilon']:.2f}")
            st.metric("Conversión $X_{s}$", f"{knee_point['Xs']*100:.3f}%")
            st.metric("$S_{out}$", f"{knee_point['Sout_ppm']:.2f} ppm")
            st.metric("Carga Horno $Q_{horno}$", f"{knee_point['Q_horno_kW']:.2f} kW")

with tab_sanity:
    st.subheader("Sanity Checks (Valores Base)")

    sc1 = evaluar_hds(
        t_in=650.0,
        epsilon=0.90,
        m_dot=100000.0,
        s_in=500.0,
        cp=2.5,
        ea=80000.0,
        k0=calcular_k0(80000.0, 0.5),
        tau=0.5,
    )
    sc2 = evaluar_hds(
        t_in=550.0,
        epsilon=0.75,
        m_dot=100000.0,
        s_in=500.0,
        cp=2.5,
        ea=80000.0,
        k0=calcular_k0(80000.0, 0.5),
        tau=0.5,
    )
    sc3 = evaluar_hds(
        t_in=600.0,
        epsilon=0.999999,
        m_dot=100000.0,
        s_in=500.0,
        cp=2.5,
        ea=80000.0,
        k0=calcular_k0(80000.0, 0.5),
        tau=0.5,
    )

    df_sanity = pd.DataFrame(
        [
            {
                "Caso": "1) Tin = 650 K, ε = 0.90",
                "Xs": f"{sc1['Xs']:.4f}",
                "Sout (ppm)": f"{sc1['Sout_ppm']:.4f}",
                "Factible": "Sí" if sc1["factible"] else "No",
                "Qhorno (kW)": f"{sc1['Q_horno_kW']:.2f}",
            },
            {
                "Caso": "2) Tin = 550 K, ε = 0.75",
                "Xs": f"{sc2['Xs']:.4f}",
                "Sout (ppm)": f"{sc2['Sout_ppm']:.4f}",
                "Factible": "Sí" if sc2["factible"] else "No",
                "Qhorno (kW)": f"{sc2['Q_horno_kW']:.2f}",
            },
            {
                "Caso": "3) Límite ε → 1 (Tin = 600 K)",
                "Xs": f"{sc3['Xs']:.4f}",
                "Sout (ppm)": f"{sc3['Sout_ppm']:.4f}",
                "Factible": "Sí" if sc3["factible"] else "No",
                "Qhorno (kW)": f"{sc3['Q_horno_kW']:.2f}",
            },
        ]
    )
    st.dataframe(df_sanity, use_container_width=True, hide_index=True)

    st.markdown("#### Estadísticas de la Malla")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Puntos Malla", f"{len(df_grid):,}")
    m2.metric("Puntos Factibles", f"{len(df_grid[df_grid['factible']]):,}")
    m3.metric("Fracción Factible", f"{(len(df_grid[df_grid['factible']])/len(df_grid))*100:.1f}%")
    m4.metric("Puntos en Pareto", f"{len(df_pareto):,}")

with tab_sensibilidad:
    st.subheader("Análisis de Sensibilidad Paramétrica")
    st.caption("Evaluado alrededor del punto seleccionado en la barra lateral.")
    df_sens = sens_cached(t_in, epsilon, m_dot, s_in, cp, ea, k0, tau)
    st.dataframe(df_sens, use_container_width=True, hide_index=True)
