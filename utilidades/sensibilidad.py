import pandas as pd

from utilidades.modelo import evaluar_hds


def calcular_sensibilidad(
    t_in_base, eps_base, m_dot_base, s_in_base, cp_base, ea_base, k0_base, tau_base
):
    caso_base = evaluar_hds(
        t_in_base, eps_base, m_dot_base, s_in_base, cp_base, ea_base, k0_base, tau_base
    )
    parametros = [
        ("m", "m_dot", m_dot_base),
        ("cp", "cp", cp_base),
        ("ea", "ea", ea_base),
        ("k0", "k0", k0_base),
        ("tau", "tau", tau_base),
    ]
    filas = []
    for nombre, clave, val_base in parametros:
        for factor, etiqueta in [(0.90, "-10%"), (1.10, "+10%")]:
            kwargs = {
                "t_in": t_in_base,
                "epsilon": eps_base,
                "m_dot": m_dot_base,
                "s_in": s_in_base,
                "cp": cp_base,
                "ea": ea_base,
                "k0": k0_base,
                "tau": tau_base,
            }
            kwargs[clave] = val_base * factor

            res = evaluar_hds(**kwargs)
            delta_q_pct = (
                ((res["Q_horno_kJ_h"] - caso_base["Q_horno_kJ_h"]) / abs(caso_base["Q_horno_kJ_h"]) * 100.0)
                if abs(caso_base["Q_horno_kJ_h"]) > 1e-9
                else 0.0
            )
            delta_s_pct = (
                ((res["Sout_ppm"] - caso_base["Sout_ppm"]) / caso_base["Sout_ppm"] * 100.0)
                if caso_base["Sout_ppm"] > 0
                else 0.0
            )

            filas.append(
                {
                    "Parámetro": nombre,
                    "Cambio": etiqueta,
                    "Q (kJ/h)": round(res["Q_horno_kJ_h"], 2),
                    "Q (kW)": round(res["Q_horno_kW"], 2),
                    "ΔQ (%)": round(delta_q_pct, 3),
                    "S_out (ppm)": round(res["Sout_ppm"], 3),
                    "ΔS_out (%)": round(delta_s_pct, 2),
                    "Factible": "Sí" if res["factible"] else "No",
                }
            )
    return pd.DataFrame(filas)


def explorar_sin(
    t_in_base, eps_base, m_dot_base, cp_base, ea_base, k0_base, tau_base, valores_sin=None
):
    if valores_sin is None:
        valores_sin = [450.0, 475.0, 500.0, 525.0, 550.0]

    filas = []
    for s_val in valores_sin:
        res = evaluar_hds(
            t_in_base, eps_base, m_dot_base, s_val, cp_base, ea_base, k0_base, tau_base
        )
        filas.append(
            {
                "S_in (ppm)": s_val,
                "X_s (%)": round(res["Xs"] * 100.0, 3),
                "S_out (ppm)": round(res["Sout_ppm"], 3),
                "Q (kJ/h)": round(res["Q_horno_kJ_h"], 2),
                "Q (kW)": round(res["Q_horno_kW"], 2),
                "Factible": "Sí" if res["factible"] else "No",
            }
        )
    return pd.DataFrame(filas)
