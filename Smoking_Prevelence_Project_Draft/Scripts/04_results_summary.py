"""Author: Matt Picaroni | Date: 2026-11-22
Purpose: Summarize observed Florida 2022 BRFSS analysis outputs.
"""
import pandas as pd
from common import DATA, RESULTS, weighted_mean

def main() -> None:
    df = pd.read_csv(DATA / "florida_2022_cleaned.csv")
    groups = pd.read_csv(RESULTS / "smoking_prevalence.csv")
    estimates = pd.read_csv(RESULTS / "statistical_results.csv")
    smoking = estimates.loc[estimates.variable=="ever_smoked"].iloc[0]
    lines = ["FLORIDA 2022 BRFSS — SMOKING AND HEART DISEASE", "",f"Complete-case sample: {len(df):,} respondents",f"Weighted overall heart disease prevalence: {100*weighted_mean(df.heart_disease,df.weight):.2f}%", "", "Weighted prevalence by smoking category:"]
    lines.extend(f"  {r.smoking_status}: {r.weighted_heart_disease_pct:.2f}% (n={int(r.n):,})" for r in groups.itertuples())
    lines.extend(["",f"Exploratory adjusted smoking odds ratio: {smoking.odds_ratio:.3f} (approx. 95% CI {smoking.ci_low:.3f}–{smoking.ci_high:.3f}); p={smoking.p_value:.4g}","", "LIMITATIONS: Cross-sectional, self-reported survey; cannot establish causality.","Weighted GLM with clustered standard errors is an approximation, not a full stratified BRFSS survey-design estimator.","The separate chi-square test is unweighted and not design-adjusted.","Missing BMI/diabetes records are excluded only from the regression model."])
    path=RESULTS / "results_summary.txt";path.write_text("\n".join(lines)+"\n")
    print("\n".join(lines))
if __name__=="__main__":
    main()
