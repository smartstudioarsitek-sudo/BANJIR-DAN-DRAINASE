import numpy as np
import pandas as pd

def mononobe_intensity(R24, tc_hours):
    """Rumus Mononobe: I = (R24/24) * (24/tc)^(2/3)"""
    return (R24 / 24.0) * ((24.0 / tc_hours) ** (2/3)) if tc_hours > 0 else 0

def nakayasu_hss(A, L, Ro=1.0, alpha=2.0):
    """HSS Nakayasu (KP-01)."""
    tg = 0.4 + 0.058 * L if L > 15 else 0.21 * (L ** 0.7)
    tr = 0.5 * tg
    tp = tg + 0.8 * tr
    t03 = alpha * tg
    qp = (A * Ro) / (3.6 * (0.3 * tp + t03))
    
    times = np.arange(0, tp + t03 * 4, 0.1)
    flows = []
    for t in times:
        if t < tp: q = qp * (t/tp)**2.4
        elif t < tp + t03: q = qp * 0.3**((t-tp)/t03)
        elif t < tp + t03 + 1.5*t03: q = qp * 0.3**((t-tp+0.5*t03)/(1.5*t03))
        else: q = qp * 0.3**((t-tp+1.5*t03)/(2*t03))
        flows.append(q)
        
    return pd.DataFrame({"Waktu (jam)": times, "Debit (m3/s)": flows}), {"Tp": tp, "Qp": qp, "T0.3": t03}