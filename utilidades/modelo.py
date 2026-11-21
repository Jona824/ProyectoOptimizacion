import numpy as np

R_GAS = 8.314
T_ALIM = 300.0
X_CALIB = 0.985
T_CALIB = 600.0
TAU_CALIB = 0.5
EA_CALIB = 80000.0
DT_AD_MAX = 15.0


def calcular_k0(
    ea: float = EA_CALIB,
    tau: float = TAU_CALIB,
    x_ref: float = X_CALIB,
    t_ref: float = T_CALIB,
) -> float:
    return -np.log(1.0 - x_ref) / (tau * np.exp(-ea / (R_GAS * t_ref)))


def evaluar_hds(t_in, epsilon, m_dot, s_in, cp, ea, k0, tau):
    k_t = k0 * np.exp(-ea / (R_GAS * t_in))
    x_s = 1.0 - np.exp(-k_t * tau)
    s_out = s_in * (1.0 - x_s)
    factible = s_out <= 10.0

    delta_t_ad = DT_AD_MAX * x_s
    t_efluente = t_in + delta_t_ad
    t_intercambiador = T_ALIM + epsilon * (t_efluente - T_ALIM)

    q_horno_kjh = m_dot * cp * (t_in - t_intercambiador)
    q_horno_kw = q_horno_kjh / 3600.0

    return {
        "Tin_K": t_in,
        "epsilon": epsilon,
        "k_h-1": k_t,
        "Xs": x_s,
        "Sout_ppm": s_out,
        "factible": factible,
        "dT_ad_K": delta_t_ad,
        "T_efluente_K": t_efluente,
        "T_intercambiador_K": t_intercambiador,
        "Q_horno_kJ_h": q_horno_kjh,
        "Q_horno_kW": q_horno_kw,
    }
