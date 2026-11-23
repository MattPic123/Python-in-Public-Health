"Author: Matt Picaroni | Date: 2026-11-22"
# Smoking and Heart Disease in Florida (2022)

HSC 4933 — Python for Health Analytics

This project examines the relationship between smoking history and reported heart disease among adults in Florida using the **2022 CDC Behavioral Risk Factor Surveillance System (BRFSS)**.

## Dataset

Download the official 2022 BRFSS SAS Transport dataset from the [CDC](https://www.cdc.gov/brfss/annual_data/annual_2022.html). Extract `LLCP2022.XPT` and put it in the project's `Data` folder. The first script keeps Florida respondents (`_STATE = 12`). 

## Set up in PyCharm

1. Open the project folder in PyCharm.
2. Select your project's working Python interpreter (`.venv`).
3. Install pandas, numpy, matplotlib, scipy, and statsmodels using Settings → Python Interpreter → Install Package.
5. Place the CDC file at `Data/LLCP2022.XPT`.

## Run the analysis

Open each file in PyCharm and click the green Run  button in this order:
`01_data_cleaning.py` 
|`02_exploratory_analysis.py` 
| `03_statistical_analysis.py` 
| `04_results_summary.py` 

`common.py` provides shared paths and calculations. Do not run it separately.


## Output files

Figures: `figures/smoking_prevalence.png`, `figures/heart_disease_by_age.png`, `figures/odds_ratios.png`.

Results: `results/smoking_prevalence.csv`, `results/age_prevalence.csv`, `results/chi_square.txt`, `results/statistical_results.csv`, `results/results_summary.txt`.

## Main findings from this run

The cleaned analysis contained 11,569 Florida respondents. Survey-weighted reported heart disease prevalence was 7.83% overall: 5.40% among never smokers, 12.20% among former smokers, and 10.70% among current smokers. In the exploratory adjusted model, having ever smoked was associated with higher odds of heart disease (OR 1.89; approximate 95% CI 1.46–2.46). Results may change if data cleaning or model settings change.

## Important limitations

BRFSS is a cross-sectional, self-reported survey. These findings show associations, not cause and effect. Prevalence estimates use survey weights, but the logistic regression with clustered standard errors is an approximation, not a fully survey-design-adjusted analysis; its confidence intervals and p-values should be interpreted cautiously. The chi-square test is unweighted and exploratory. The regression also excludes respondents missing BMI or diabetes information.

## Reference

Centers for Disease Control and Prevention (CDC). Behavioral Risk Factor Surveillance System: 2022 Annual Survey Data. https://www.cdc.gov/brfss/annual_data/annual_2022.html

