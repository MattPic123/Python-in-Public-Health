"""Author: Matt Picaroni | Date: 2026-11-22
Purpose: Exploratory chi-square and weighted logistic regression with PSU-clustered SE.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency
import statsmodels.api as sm
from common import DATA, FIGURES, RESULTS

def main() -> None:
    df = pd.read_csv(DATA / "florida_2022_cleaned.csv")
    contingency = pd.crosstab(df.ever_smoked,df.heart_disease)
    chi2,p,_,_ = chi2_contingency(contingency)
    # Unweighted chi-square is illustrative only; not design-adjusted.
    (RESULTS / "chi_square.txt").write_text(f"UNWEIGHTED exploratory chi-square: statistic={chi2:.4f}; p={p:.6g}\nNot design-adjusted.\n")
    model_df = df.dropna(subset=["bmi","diabetes"]).copy()
    if len(model_df)<50 or model_df.heart_disease.nunique()<2:
        raise ValueError("Insufficient valid observations for logistic regression")
    x = pd.DataFrame({"ever_smoked":model_df.ever_smoked.astype(float),"age_group":model_df.age_group.astype(float),"bmi":model_df.bmi.astype(float),"diabetes":model_df.diabetes.astype(float),"female":(model_df.sex=="Female").astype(float)})
    x = sm.add_constant(x)
    # Scale weights to average 1 to avoid extremely large pseudo-sample sizes.
    weights = model_df.weight / model_df.weight.mean()
    # PSUs are identified within strata; construct a unique cluster identifier.
    cluster = model_df.stratum.astype(str) + "_" + model_df.psu.astype(str)
    fit = sm.GLM(model_df.heart_disease,x,family=sm.families.Binomial(),freq_weights=weights).fit(cov_type="cluster",cov_kwds={"groups":cluster})
    ci = fit.conf_int()
    result = pd.DataFrame({"variable":fit.params.index,"odds_ratio":np.exp(fit.params),"ci_low":np.exp(ci[0]),"ci_high":np.exp(ci[1]),"p_value":fit.pvalues})
    result.to_csv(RESULTS / "statistical_results.csv",index=False)
    display = result[result.variable!="const"].iloc[::-1]
    fig,ax=plt.subplots(figsize=(9,5))
    y=np.arange(len(display))
    ax.errorbar(display.odds_ratio,y,xerr=[display.odds_ratio-display.ci_low,display.ci_high-display.odds_ratio],fmt="o",capsize=3)
    ax.axvline(1,linestyle="--",color="gray")
    ax.set_yticks(y,display.variable);ax.set_xlabel("Adjusted odds ratio (approximate 95% CI)")
    ax.set_title("Florida BRFSS 2022: exploratory weighted logistic regression")
    plt.tight_layout();plt.savefig(FIGURES / "odds_ratios.png",dpi=200);plt.close()
    print(result.to_string(index=False));print("NOTE: Cluster-robust weighted GLM is not full complex-survey inference.")
if __name__ == "__main__":
    main()
