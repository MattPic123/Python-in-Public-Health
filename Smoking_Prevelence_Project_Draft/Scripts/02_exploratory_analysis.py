"""Author: Matt Picaroni | Date: 2026-11-22
Purpose: Survey-weighted descriptive comparisons for Florida BRFSS 2022.
"""
import pandas as pd
import matplotlib.pyplot as plt
from common import DATA, FIGURES, RESULTS, weighted_mean

def main() -> None:
    df = pd.read_csv(DATA / "florida_2022_cleaned.csv")
    rows = []
    for name, group in df.groupby("smoking_status"):
        rows.append({"smoking_status":name,"n":len(group),"weighted_heart_disease_pct":100*weighted_mean(group.heart_disease,group.weight)})
    table = pd.DataFrame(rows).set_index("smoking_status").reindex(["Never","Former","Current"])
    table.to_csv(RESULTS / "smoking_prevalence.csv")
    ax = table.weighted_heart_disease_pct.plot.bar(figsize=(8,5),rot=0)
    ax.set(ylabel="Survey-weighted heart disease prevalence (%)",xlabel="Smoking status",title="Florida adults, 2022 BRFSS")
    plt.tight_layout();plt.savefig(FIGURES / "smoking_prevalence.png",dpi=200);plt.close()
    rows = []
    for age, group in df.groupby("age_group"):
        rows.append({"age_group":int(age),"n":len(group),"weighted_heart_disease_pct":100*weighted_mean(group.heart_disease,group.weight)})
    ages = pd.DataFrame(rows).sort_values("age_group")
    ages.to_csv(RESULTS / "age_prevalence.csv",index=False)
    ax = ages.plot.bar(x="age_group",y="weighted_heart_disease_pct",legend=False,figsize=(9,5))
    ax.set(xlabel="CDC five-year age category (1=18–24; 13=80+)",ylabel="Survey-weighted prevalence (%)",title="Heart disease by age: Florida, 2022")
    plt.tight_layout();plt.savefig(FIGURES / "heart_disease_by_age.png",dpi=200);plt.close()
    print(table.round(2).to_string());print("Figures and tables saved.")
if __name__ == "__main__":
    main()
