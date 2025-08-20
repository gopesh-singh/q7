# analysis.py
from pathlib import Path
import math
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "mrr_growth_2024.csv"
VIS_DIR = ROOT / "visuals"
VIS_DIR.mkdir(parents=True, exist_ok=True)
OUT_SUMMARY = ROOT / "analysis" / "summary.csv"

def load_data():
    df = pd.read_csv(DATA_PATH)
    required_cols = {"quarter", "value"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV must include columns: {required_cols}")
    return df

def compute_average(df):
    q = df[df["quarter"].isin(["Q1", "Q2", "Q3", "Q4"])].copy()
    return round(q["value"].mean(), 2)

def get_industry_target(df):
    row = df.loc[df["quarter"] == "IndustryTarget", "value"]
    return float(row.iloc) if not row.empty else 15.0

def validate_average(df):
    provided = df.loc[df["quarter"] == "Average", "value"]
    if provided.empty:
        raise ValueError("Average row not found in CSV.")
    provided_avg = float(provided.iloc)
    computed_avg = compute_average(df)
    if not math.isclose(computed_avg, provided_avg, rel_tol=1e-03, abs_tol=1e-03):
        raise AssertionError(f"Average mismatch: computed {computed_avg}, provided {provided_avg}")
    return provided_avg, computed_avg

def save_summary(df):
    avg = compute_average(df)
    target = get_industry_target(df)
    gap = round(target - avg, 2)
    summary = pd.DataFrame([{
        "average_mrr_growth": avg,
        "industry_target": target,
        "gap_to_target": gap,
        "meets_target": avg >= target
    }])
    OUT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUT_SUMMARY, index=False)
    print(summary.to_string(index=False))

def plot_trend(df):
    q = df[df["quarter"].isin(["Q1", "Q2", "Q3", "Q4"])].copy()
    target = get_industry_target(df)
    sns.set(style="whitegrid")
    plt.figure(figsize=(8, 4.5))
    ax = sns.lineplot(x="quarter", y="value", data=q, marker="o", linewidth=2, color="#2b8a3e")
    plt.axhline(y=target, color="#d9480f", linestyle="--", linewidth=1.5, label=f"Target {target}%")
    for x, y in zip(q["quarter"], q["value"]):
        ax.annotate(f"{y:.2f}%", xy=(x, y), xytext=(0, 6), textcoords="offset points", ha="center", fontsize=9)
    ax.set_title("2024 Quarterly MRR Growth (%)")
    ax.set_xlabel("Quarter")
    ax.set_ylabel("Growth (%)")
    plt.legend()
    out = VIS_DIR / "mrr_trend.png"
    plt.tight_layout()
    plt.savefig(out, dpi=200)
    plt.close()
    print(f"Saved: {out}")

def plot_avg_vs_target(df):
    avg = compute_average(df)
    target = get_industry_target(df)
    comp = pd.DataFrame({"Metric": ["Average 2024", "Industry Target"], "Value": [avg, target]})
    sns.set(style="whitegrid")
    plt.figure(figsize=(6, 4.5))
    ax = sns.barplot(x="Metric", y="Value", data=comp, palette=["#1f78b4", "#d9480f"])
    for p in ax.patches:
        h = p.get_height()
        ax.annotate(f"{h:.2f}%", (p.get_x() + p.get_width()/2, h), ha="center", va="bottom",
                    fontsize=10, xytext=(0, 3), textcoords="offset points")
    ax.set_title("MRR Growth: Average vs. Industry Target")
    ax.set_xlabel("")
    ax.set_ylabel("Growth (%)")
    out = VIS_DIR / "avg_vs_target.png"
    plt.tight_layout()
    plt.savefig(out, dpi=200)
    plt.close()
    print(f"Saved: {out}")

def main():
    df = load_data()
    provided_avg, computed_avg = validate_average(df)
    print(f"Average validated: provided={provided_avg:.2f}, computed={computed_avg:.2f}")
    save_summary(df)
    plot_trend(df)
    plot_avg_vs_target(df)
    print("Done.")

if __name__ == "__main__":
    main()
