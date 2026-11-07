import pandas as pd
import numpy as np
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)

YEARS = [2023, 2024, 2025, 2026]
MIN_N = 20

def load_subject(path, sheet, tag):
    d = pd.read_excel(path, sheet_name=sheet)
    print(f"[{tag}] raw rows: {len(d):,}")

    d["Grade"] = d["Grade"].astype(str)
    d = d[(d["Grade"] == "All Grades") & (d["Year"].isin(YEARS))].copy()
    print(f"[{tag}] after filtering: {len(d):,}")
    print(f"[{tag}] duplicate school-years: {d.duplicated(['DBN', 'Year']).sum()}")

    num_cols = ["Number Tested", "# Level 1", "# Level 2", "# Level 3",
                "# Level 4", "# Level 3+4", "% Level 3+4"]

    is_s = d[num_cols].astype(str).apply(lambda col: col.str.strip().str.lower() == "s")
    print(f"[{tag}] rows with suppressed values: {is_s.any(axis=1).sum()}")

    for c in num_cols:
        d[c] = pd.to_numeric(d[c], errors="coerce")

    levels_total = d[["# Level 1", "# Level 2", "# Level 3", "# Level 4"]].sum(axis=1)
    mismatch = ((levels_total - d["Number Tested"]).abs() > 0) & d["# Level 1"].notna()
    print(f"[{tag}] rows where level counts != tested (excluding suppressed): {mismatch.sum()}")

    recomputed = 100 * d["# Level 3+4"] / d["Number Tested"]
    print(f"[{tag}] max gap reported vs recomputed %: {(recomputed - d['% Level 3+4']).abs().max():.4f}")

    d = d[d["Number Tested"] >= MIN_N].dropna(subset=["# Level 3+4"])
    print(f"[{tag}] kept: {len(d):,}")

    d = d[["DBN", "School Name", "Year", "Number Tested", "# Level 3+4"]]
    return d.rename(columns={"Number Tested": f"n_{tag}", "# Level 3+4": f"k_{tag}"})

ela = load_subject("data/school-ela-results-public.xlsx", "ELA - All", "ela")
mat = load_subject("data/school-math-results-public.xlsx", "Math - All", "math")

df = ela.merge(mat.drop(columns="School Name"), on=["DBN", "Year"], how="inner")
df["p_ela"] = df["k_ela"] / df["n_ela"]
df["p_math"] = df["k_math"] / df["n_math"]

print(f"[merge] school-years with both subjects: {len(df):,}")
print(f"[merge] ELA rows dropped: {len(ela) - len(df)}, Math rows dropped: {len(mat) - len(df)}")
print(f"[merge] schools in 2026: {df[df['Year'] == 2026].shape[0]}")
print(df.head())

def score(d, w=(0.5, 0.5), use_shrink=True, verbose=False):
    d = d.copy()
    for s in ["ela", "math"]:
        gm = d[f"k_{s}"].sum() / d[f"n_{s}"].sum()
        noise = gm * (1 - gm) / d[f"n_{s}"]
        tau2 = max(d[f"p_{s}"].var() - noise.mean(), 1e-4)
        B = tau2 / (tau2 + noise)
        if verbose:
            print(f"[shrink] {s}: citywide rate {gm:.3f}, between-school variance {tau2:.4f}")

        if use_shrink:
            d[f"adj_{s}"] = gm + B * (d[f"p_{s}"] - gm)
        else:
            d[f"adj_{s}"] = d[f"p_{s}"]

        d[f"z_{s}"] = (d[f"adj_{s}"] - d[f"adj_{s}"].mean()) / d[f"adj_{s}"].std()

    d["z"] = w[0] * d["z_ela"] + w[1] * d["z_math"]
    d["rank"] = d["z"].rank(ascending=False, method="min").astype(int)
    return d

cur = score(df[df["Year"] == 2026], verbose=True)
print(f"[rank] schools ranked in 2026: {len(cur)}")
print(cur.sort_values("rank").head(10)[["School Name", "p_ela", "p_math", "z", "rank"]])
print("z_ela mean and std:", round(cur["z_ela"].mean(), 3), round(cur["z_ela"].std(), 3))


rng = np.random.default_rng(42)
d = cur.reset_index(drop=True)
N_SIMS = 100
sims = np.zeros((len(d), N_SIMS))

for i in range(N_SIMS):
    t = d.copy()
    t["k_ela"] = rng.binomial(t["n_ela"], t["adj_ela"])
    t["k_math"] = rng.binomial(t["n_math"], t["adj_math"])
    t["p_ela"] = t["k_ela"] / t["n_ela"]
    t["p_math"] = t["k_math"] / t["n_math"]
    sims[:, i] = score(t)["rank"].values

d["lo"] = np.percentile(sims, 5, axis=1)
d["hi"] = np.percentile(sims, 95, axis=1)
d["range_width"] = d["hi"] - d["lo"]

print(f"[uncertainty] median 90% rank range: {d['range_width'].median():.0f} places")
print(d.groupby(pd.cut(d["rank"], [0, 10, 100, 500, 900, 1200]), observed=True)["range_width"].median().round(0))

from scipy.stats import spearmanr

d26 = df[df["Year"] == 2026]
base = cur.set_index("DBN")["rank"]

variants = {
    "No small-school adjustment": score(d26, use_shrink=False),
    "ELA-heavy 60/40": score(d26, w=(0.6, 0.4)),
    "Math-heavy 40/60": score(d26, w=(0.4, 0.6)),
}

print("[sensitivity] compared with the baseline ranking:")
for name, v in variants.items():
    r = v.set_index("DBN")["rank"].reindex(base.index)
    corr = spearmanr(base, r)[0]
    overlap = len(set(base[base <= 100].index) & set(r[r <= 100].index))
    moved = ((base - r).abs() >= 50).sum()
    print(f"  {name}: rank correlation {corr:.3f}, top-100 overlap {overlap}, schools moving 50+ places {moved}")

    borough_map = {"M": "Manhattan", "X": "Bronx", "K": "Brooklyn", "Q": "Queens", "R": "Staten Island"}
d["borough"] = d["DBN"].str[2].map(borough_map)

out = d.sort_values("rank")[["rank", "DBN", "School Name", "borough", "n_ela", "n_math", "p_ela", "p_math", "z", "lo", "hi"]]
out = out.round({"p_ela": 3, "p_math": 3, "z": 3, "lo": 0, "hi": 0})
out.to_csv("school_rankings_2026.csv", index=False)

print(f"[export] saved {len(out)} schools to school_rankings_2026.csv")
print(out.head())

print(d.groupby("borough")["z"].median().round(2))
print(d[d["rank"] <= 100]["borough"].value_counts())
print("share of schools with rank range <= 50:", round((d["range_width"] <= 50).mean(), 2))

summary = d.groupby("borough").agg(schools=("z", "size"), top100=("rank", lambda s: (s <= 100).sum()))
summary["pct_top100"] = (100 * summary["top100"] / summary["schools"]).round(1)
print(summary)