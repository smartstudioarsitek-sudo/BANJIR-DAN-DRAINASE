import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.frequency import log_pearson_iii, gumbel_method, goodness_of_fit
from utils.hydrology import nakayasu_hss, mononobe_intensity
from utils.drainage import check_pipe

st.set_page_config(page_title="Smart Smada PU-Ready", layout="wide")
st.title("🌊 Smart Smada: Edisi Standar PU (SNI 2415:2016)")

tab1, tab2, tab3 = st.tabs(["Analisis Frekuensi", "HSS Nakayasu", "Drainase"])

# --- TAB 1 ---
with tab1:
    uploaded = st.file_uploader("Upload CSV (Tahun, Hujan)", type="csv")
    if uploaded:
        df = pd.read_csv(uploaded)
        rain = df.iloc[:, 1].values
        periods = [2, 5, 10, 25, 50, 100]
        
        lp3_res, _ = log_pearson_iii(rain, periods)
        fit = goodness_of_fit(rain, 'log_pearson3')
        
        st.subheader("Hasil Log Pearson III")
        st.table(pd.DataFrame(lp3_res.items(), columns=["Tahun", "Hujan (mm)"]))
        st.write(f"**Uji KS:** {fit['KS_Res']} (Stat: {fit['KS_Stat']:.3f})")
        st.write(f"**Uji Chi:** {fit['Chi_Res']} (Stat: {fit['Chi_Stat']:.3f})")
        st.session_state['r24'] = lp3_res[25] # Default Tr 25

# --- TAB 2 ---
with tab2:
    A = st.number_input("Luas DAS (km2)", value=10.0)
    L = st.number_input("Panjang Sungai (km)", value=5.0)
    if st.button("Hitung Nakayasu"):
        r24 = st.session_state.get('r24', 100)
        df_hss, p = nakayasu_hss(A, L, Ro=1.0)
        # Sederhana: Q_banjir = HSS * R_efektif (misal C=0.6)
        df_hss["Debit (m3/s)"] *= (r24 * 0.6) 
        
        fig, ax = plt.subplots()
        ax.plot(df_hss["Waktu (jam)"], df_hss["Debit (m3/s)"])
        ax.set_title("Hidrograf Banjir Rencana")
        st.pyplot(fig)
        st.metric("Debit Puncak", f"{df_hss['Debit (m3/s)'].max():.2f} m3/s")

# --- TAB 3 ---
with tab3:
    col1, col2 = st.columns(2)
    with col1:
        A_ha = st.number_input("Luas Lahan (Ha)", value=2.0)
        tc = st.number_input("tc (menit)", value=15.0)
    with col2:
        S = st.number_input("Kemiringan (S)", value=0.01)
        D = st.selectbox("Diameter Pipa (m)", [0.3, 0.4, 0.5, 0.6, 0.8, 1.0])
    
    if st.button("Cek Kapasitas"):
        r24 = st.session_state.get('r24', 100)
        I = mononobe_intensity(r24, tc/60)
        Q_des = 0.278 * 0.7 * I * (A_ha/100)
        res = check_pipe(D, S, 0.013, Q_des)
        
        st.metric("Debit Desain", f"{Q_des:.3f} m3/s")
        st.write(f"**Status:** {res['Status']} (Rasio: {res['Ratio']:.1f}%)")