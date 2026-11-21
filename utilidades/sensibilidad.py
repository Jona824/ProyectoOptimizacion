Python
import pandas as pd

from modelo import calcular_k0, evaluar_hds


def calcular_sensibilidad(
    t_in_base, eps_base, m_dot_base, s_in_base, cp_base, ea_base, k0_base, tau_base
):
    caso_base = evaluar_hds(
        t_in_base, eps_base, m_dot_base, s_in_base, cp_base, ea_base, k0_base, tau_base
    )
    parametros = [
        ("Flujo másico (ṁ)", "m_dot", m_dot_base),
        ("Capacidad calorífica (Cp)", "cp", cp_base),
        ("Energía de activación (Ea)", "ea", ea_base),
        ("Factor preexponencial (k0)", "k0", k0_base),
        ("Tiempo espacial (τ)", "tau", tau_base),
        ("Efectividad (ε)", "epsilon", eps_base),
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
            val_pert = val_base * factor
            if clave == "epsilon":
                val_pert = min(max(val_pert, 0.0), 1.0)
            kwargs[clave] = val_pert

            if clave in ["ea", "tau"]:
                kwargs["k0"] = calcular_k0(kwargs["ea"], kwargs["tau"])

            res = evaluar_hds(**kwargs)
            delta_q_pct = (
                ((res["Q_horno_kW"] - caso_base["Q_horno_kW"]) / abs(caso_base["Q_horno_kW"]) * 100.0)
                if abs(caso_base["Q_horno_kW"]) > 1e-9
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
                    "Perturbación": etiqueta,
                    "Valor": f"{val_pert:.4g}",
                    "Qhorno (kW)": round(res["Q_horno_kW"], 2),
                    "ΔQhorno (%)": round(delta_q_pct, 2),
                    "Sout (ppm)": round(res["Sout_ppm"], 3),
                    "ΔSout (%)": round(delta_s_pct, 2),
                    "Factible": "Sí" if res["factible"] else "No",
                }
            )
    return pd.DataFrame(filas)
