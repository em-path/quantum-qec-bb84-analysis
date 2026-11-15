"""
Generate the figures for the research project.

Produces:
    - figs/qber_vs_p.png                  -> QBER vs p for n = 1, 3, 5, 7
    - figs/tasa_efectiva_vs_p.png         -> effective rate vs p for n = 1, 3, 5, 7
    - figs/mapa_calor.png                 -> heatmap of effective rate over p x n
    - data/optimal_n.csv                  -> optimal n for each noise level
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================
# ACADEMIC STYLE CONFIGURATION
# ============================================================

plt.rcParams.update({
    "figure.figsize": (8, 5),
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "legend.fontsize": 10,
    "lines.linewidth": 2,
    "lines.markersize": 6,
    "grid.alpha": 0.3,
    "savefig.bbox": "tight",
})

COLORS = {
    1: "#d62728",   # red
    3: "#1f77b4",   # blue
    5: "#2ca02c",   # green
    7: "#9467bd",   # purple
}

MARKERS = {1: "o", 3: "s", 5: "^", 7: "D"}


# ============================================================
# DATA LOADING
# ============================================================

CSV_PATH = "data/final_results.csv"
FIGS_PATH = "figs"

os.makedirs(FIGS_PATH, exist_ok=True)

# Accept both the legacy Spanish column names and the English ones so that
# previously generated result files remain compatible.
COLUMN_MAP = {
    "n_cribado": "n_sifted",
    "tasa_bruta": "gross_rate",
    "tasa_efectiva": "effective_rate",
}

df = pd.read_csv(CSV_PATH).rename(columns=COLUMN_MAP)

# BB84 security threshold (QBER = 0.11)
QBER_THRESHOLD = 0.11

print(f"Data loaded: {len(df)} rows")
print(f"Values of p: {sorted(df['p'].unique())}")
print(f"Values of n: {sorted(df['n'].unique())}")


# ============================================================
# FIGURE 1: QBER vs p
# ============================================================

fig, ax = plt.subplots()

for n in [1, 3, 5, 7]:
    subset = df[df["n"] == n].sort_values("p")
    ax.plot(subset["p"], subset["qber"],
            marker=MARKERS[n],
            color=COLORS[n],
            label=f"$n = {n}$",
            markersize=7)

# Security threshold line
ax.axhline(y=QBER_THRESHOLD, color="red", linestyle="--",
           linewidth=1.5, label="Security threshold (QBER = 0.11)")

ax.set_xlabel("Error probability per qubit, $p$")
ax.set_ylabel("QBER")
ax.set_title("QBER with and without quantum error correction")
ax.legend(loc="upper left")
ax.grid(True, alpha=0.3)

plt.savefig(f"{FIGS_PATH}/qber_vs_p.png")
plt.close()
print("Saved: figs/qber_vs_p.png")


# ============================================================
# FIGURE 2: Effective rate vs p (the key figure)
# ============================================================

fig, ax = plt.subplots()

for n in [1, 3, 5, 7]:
    subset = df[df["n"] == n].sort_values("p")
    ax.plot(subset["p"], subset["effective_rate"],
            marker=MARKERS[n],
            color=COLORS[n],
            label=f"$n = {n}$",
            markersize=7)

ax.set_xlabel("Error probability per qubit, $p$")
ax.set_ylabel(r"Effective secret-key rate, $R_{\mathrm{effective}}$")
ax.set_title("Trade-off between error correction and qubit overhead")
ax.grid(True, alpha=0.3)

# Transition annotation
ax.axvspan(0.10, 0.12, alpha=0.15, color="orange",
           label="Transition")
ax.legend(loc="upper right")

plt.savefig(f"{FIGS_PATH}/tasa_efectiva_vs_p.png")
plt.close()
print("Saved: figs/tasa_efectiva_vs_p.png")


# ============================================================
# FIGURE 3: Heatmap of p x n
# ============================================================

# Pivot data: rows = n, columns = p, values = effective_rate
pivot = df.pivot(index="n", columns="p", values="effective_rate")

fig, ax = plt.subplots(figsize=(11, 4))

sns.heatmap(
    pivot,
    annot=True,
    fmt=".3f",
    cmap="viridis",
    cbar_kws={"label": r"$R_{\mathrm{effective}}$"},
    linewidths=0.5,
    linecolor="white",
    ax=ax,
    annot_kws={"size": 8},
)

ax.set_xlabel("Error probability per qubit, $p$")
ax.set_ylabel("Code size, $n$")
ax.set_title("Effective secret-key rate as a function of $(p, n)$")

plt.savefig(f"{FIGS_PATH}/mapa_calor.png")
plt.close()
print("Saved: figs/mapa_calor.png")


# ============================================================
# FIGURE 4 (EXTRA): optimal n for each noise level
# ============================================================

# For each p, find the n that maximizes the effective rate
optima = []
for p in sorted(df["p"].unique()):
    subset = df[df["p"] == p]
    best_index = subset["effective_rate"].idxmax()
    optimal_n = int(subset.loc[best_index, "n"])
    optimal_rate = subset.loc[best_index, "effective_rate"]
    optima.append({
        "p": p,
        "optimal_n": optimal_n,
        "optimal_effective_rate": optimal_rate,
    })

df_opt = pd.DataFrame(optima)
df_opt.to_csv("data/optimal_n.csv", index=False)

print()
print("=" * 50)
print("OPTIMAL CODE FOR EACH NOISE LEVEL")
print("=" * 50)
print(f"{'p':>6} | {'optimal_n':>9} | {'R_effective':>12}")
print("-" * 50)
for _, row in df_opt.iterrows():
    print(f"{row['p']:>6.2f} | {row['optimal_n']:>9} | "
          f"{row['optimal_effective_rate']:>12.4f}")
print("=" * 50)

print()
print("Figures generated successfully.")
print(f"Location: {FIGS_PATH}/")
