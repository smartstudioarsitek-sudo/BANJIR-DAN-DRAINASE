import numpy as np
import pandas as pd
from scipy import stats

def calculate_statistics(data):
    """Menghitung parameter statistik dasar."""
    n = len(data)
    mean = np.mean(data)
    std = np.std(data, ddof=1)
    skew = stats.skew(data, bias=False)
    return {"n": n, "mean": mean, "std": std, "skew": skew}

def log_pearson_iii(data, return_periods):
    """Analisis Log Pearson Type III sesuai SNI 2415:2016."""
    log_data = np.log10(data)
    stats_p = calculate_statistics(log_data)
    results = {}
    for tr in return_periods:
        prob = 1.0 / tr
        # K-Factor menggunakan ppf (Percent Point Function) dari Pearson3
        k_val = stats.pearson3.ppf(1 - prob, skew=stats_p['skew'])
        log_qt = stats_p['mean'] + k_val * stats_p['std']
        results[tr] = 10**log_qt
    return results, stats_p

def gumbel_method(data, return_periods):
    """Analisis Distribusi Gumbel."""
    loc, scale = stats.gumbel_r.fit(data)
    stats_p = calculate_statistics(data)
    results = {tr: stats.gumbel_r.isf(1.0/tr, loc=loc, scale=scale) for tr in return_periods}
    return results, stats_p

def goodness_of_fit(data, dist_type='log_pearson3'):
    """Uji Chi-Square dan Smirnov-Kolmogorov."""
    n = len(data)
    if dist_type == 'log_pearson3':
        test_data = np.sort(np.log10(data))
        stats_p = calculate_statistics(test_data)
        dist_func = lambda x: stats.pearson3.cdf(x, skew=stats_p['skew'], loc=stats_p['mean'], scale=stats_p['std'])
    else:
        test_data = np.sort(data)
        loc, scale = stats.gumbel_r.fit(data)
        dist_func = lambda x: stats.gumbel_r.cdf(x, loc=loc, scale=scale)

    # 1. Smirnov-Kolmogorov
    d_stat, _ = stats.kstest(test_data, dist_func)
    d_critical = 1.36 / np.sqrt(n)
    ks_res = "DITERIMA" if d_stat < d_critical else "DITOLAK"

    # 2. Chi-Square
    num_bins = int(1 + 3.3 * np.log10(n))
    obs_freq, bin_edges = np.histogram(test_data, bins=num_bins)
    exp_freq = []
    for i in range(num_bins):
        prob = dist_func(bin_edges[i+1]) - dist_func(bin_edges[i])
        exp_freq.append(prob * n)
    
    exp_freq = np.array(exp_freq)
    if np.sum(exp_freq) > 0: exp_freq *= (n / np.sum(exp_freq))
    
    chi_stat, _ = stats.chisquare(obs_freq, f_exp=exp_freq)
    chi_crit = stats.chi2.ppf(0.95, max(1, num_bins - 3))
    chi_res = "DITERIMA" if chi_stat < chi_crit else "DITOLAK"

    return {"KS_Stat": d_stat, "KS_Crit": d_critical, "KS_Res": ks_res,
            "Chi_Stat": chi_stat, "Chi_Crit": chi_crit, "Chi_Res": chi_res}