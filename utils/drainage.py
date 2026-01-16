import numpy as np

def check_pipe(diameter, slope, n, Q_design):
    """Cek Kapasitas Pipa sesuai Permen PUPR 12/2014."""
    R_full = diameter / 4.0
    A_full = np.pi * (diameter/2)**2
    V_full = (1/n) * (R_full**(2/3)) * (slope**0.5)
    Q_full = A_full * V_full
    ratio = (Q_design / Q_full) * 100
    
    if ratio > 100: status = "BAHAYA (Meluap)"
    elif ratio > 85: status = "KRITIS (Butuh Freeboard)"
    else: status = "AMAN"
    
    return {"Q_full": Q_full, "V_full": V_full, "Ratio": ratio, "Status": status}