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
        for factor, etiqueta in [(0.90, "-10"), (1.10, "+10")]:
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
                    "Cambio (%)": etiqueta,
                    "Q (kJ/h)": f"{res['Q_horno_kJ_h']:.4e}",
                    "ΔQ (%)": f"{delta_q_pct:+.3f}",
                    "S_out (ppm)": f"{res['Sout_ppm']:.3f}",
                    "ΔS_out (%)": f"{delta_s_pct:+.1f}",
                    "¿Factible?": bool(res["factible"]),
                }
            )
    return pd.DataFrame(filas)
