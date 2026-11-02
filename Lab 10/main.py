# =============================================================================
# Author: Matthew Picaroni
# Assignment: Kaplan-Meier Log-Rank and Cox Proportional Hazards Analyses
# Purpose: Analyze heart failure readmission and survival using CSV datasets.
# =============================================================================

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter, KaplanMeierFitter
from lifelines.statistics import logrank_test, proportional_hazard_test


# Use the script's folder regardless of the working directory.
BASE_FOLDER = Path(__file__).resolve().parent
OUTPUT_FOLDER = BASE_FOLDER / "figures"
OUTPUT_FOLDER.mkdir(exist_ok=True)


def load_dataset(filename, required_columns, time_column, event_column, cutoff):
    """Load a CSV, inspect its structure, and validate analysis columns."""
    file_path = BASE_FOLDER / filename

    if not file_path.is_file():
        raise FileNotFoundError(f"Place {filename} in {BASE_FOLDER}")

    data = pd.read_csv(file_path)

    missing_columns = set(required_columns) - set(data.columns)
    if missing_columns:
        raise ValueError(f"{filename}: missing columns {sorted(missing_columns)}")

    print(f"\nDataset: {filename}")
    print(f"Number of records: {len(data)}")
    print("\nColumn data types:")
    print(data.dtypes)
    print("\nMissing values by column:")
    print(data.isna().sum())

    if data[required_columns].isna().any().any():
        raise ValueError(f"{filename}: required columns contain missing values.")

    if not data[event_column].isin([0, 1]).all():
        raise ValueError(f"{event_column} must contain only 0 and 1.")

    times = pd.to_numeric(data[time_column], errors="raise")
    if not np.isfinite(times).all() or not times.between(0, cutoff).all():
        raise ValueError(f"{time_column} must be between 0 and {cutoff}.")

    data[time_column] = times
    return data


def run_logrank_analysis():
    """Compare readmission-free survival by treatment group and sex."""
    required_columns = [
        "treatment_group", "sex", "time_days", "readmitted"
    ]

    data = load_dataset(
        "km_logrank_readmission.csv",
        required_columns,
        "time_days",
        "readmitted",
        180,
    )

    comparisons = [
        ("treatment_group", "Treatment group"),
        ("sex", "Sex"),
    ]

    figure, axes = plt.subplots(1, 2, figsize=(14, 6))

    for axis, (group_column, title) in zip(axes, comparisons):
        groups = sorted(data[group_column].unique())

        if len(groups) != 2:
            raise ValueError(f"{group_column} must contain exactly two groups.")

        first_group = data.loc[data[group_column] == groups[0]]
        second_group = data.loc[data[group_column] == groups[1]]

        # Event indicators allow the test to account for right censoring.
        result = logrank_test(
            first_group["time_days"],
            second_group["time_days"],
            event_observed_A=first_group["readmitted"],
            event_observed_B=second_group["readmitted"],
        )

        print(f"\nLog-rank test by {group_column}:")
        result.print_summary()

        for group_name in groups:
            group_data = data.loc[data[group_column] == group_name]
            event_count = int(group_data["readmitted"].sum())

            estimator = KaplanMeierFitter()
            estimator.fit(
                durations=group_data["time_days"],
                event_observed=group_data["readmitted"],
                label=(
                    f"{group_name} "
                    f"(n={len(group_data)}, events={event_count})"
                ),
            )

            estimator.plot_survival_function(
                ax=axis,
                ci_show=True,
                show_censors=True,
            )

        axis.set_title(
            f"{title}\n"
            f"Log-rank chi-square = {result.test_statistic:.3f}, "
            f"p = {result.p_value:.4g}"
        )
        axis.set_xlabel("Days after discharge")
        axis.set_ylabel("Probability of remaining readmission-free")
        axis.set_xlim(0, 180)
        axis.set_ylim(0, 1.02)
        axis.grid(alpha=0.25)
        axis.legend(fontsize=8, loc="lower left")

    figure.suptitle(
        "Kaplan-Meier Analysis: Heart Failure Readmission",
        fontsize=15,
    )
    figure.text(
        0.5,
        0.02,
        "Shaded bands: 95% confidence intervals. "
        "Tick marks: censored observations.",
        ha="center",
        fontsize=9,
    )
    figure.tight_layout(rect=(0, 0.05, 1, 0.93))

    output_path = OUTPUT_FOLDER / "km_logrank_readmission.png"
    figure.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"\nSaved figure: {output_path}")

    plt.show()
    plt.close(figure)


def run_cox_analysis():
    """Model time to all-cause death using all ten supplied covariates."""
    covariates = [
        "age",
        "sex",
        "bmi",
        "systolic_bp",
        "ejection_fraction",
        "diabetes",
        "smoker",
        "chronic_kidney_disease",
        "nyha_class",
        "beta_blocker",
    ]

    data = load_dataset(
        "cox_ph_heart_failure_survival.csv",
        ["time_months", "death"] + covariates,
        "time_months",
        "death",
        36,
    )

    # The supplied CSV uses text labels for sex.
    # Encode Male = 1 and Female = 0; Female is the reference group.
    if not data["sex"].isin(["Male", "Female"]).all():
        raise ValueError("The sex column must contain Male or Female.")

    data["sex"] = data["sex"].map({"Female": 0, "Male": 1})

    binary_columns = [
        "sex", "diabetes", "smoker", "chronic_kidney_disease", "beta_blocker"
    ]
    for column in binary_columns:
        if not data[column].isin([0, 1]).all():
            raise ValueError(f"{column} must contain only 0 and 1.")

    if not data["nyha_class"].isin([1, 2, 3, 4]).all():
        raise ValueError("nyha_class must contain values from 1 through 4.")

    # Select analysis columns explicitly so patient_id is never a predictor.
    model_data = data[["time_months", "death"] + covariates].copy()
    model_data = model_data.apply(pd.to_numeric, errors="raise")

    if not np.isfinite(model_data.to_numpy()).all():
        raise ValueError("The Cox model contains non-finite values.")

    # NYHA class is modeled as an ordinal, one-class increase.
    model = CoxPHFitter()
    model.fit(
        model_data,
        duration_col="time_months",
        event_col="death",
    )

    print("\nCox proportional hazards model:")
    model.print_summary()

    overall_test = model.log_likelihood_ratio_test()
    print("\nOverall model likelihood-ratio test:")
    overall_test.print_summary()

    # Assess the PH assumption using a rank-based Schoenfeld residual test.
    # Small p-values suggest a possible violation for that covariate.
    assumption_test = proportional_hazard_test(
        model,
        model_data,
        time_transform="rank",
    )
    print("\nProportional hazards assumption tests:")
    assumption_test.print_summary()

    summary = model.summary.loc[covariates]
    hazard_ratios = summary["exp(coef)"]
    lower_limits = summary["exp(coef) lower 95%"]
    upper_limits = summary["exp(coef) upper 95%"]

    labels = [
        "Age (+1 year)",
        "Male vs. Female",
        "BMI (+1 unit)",
        "Systolic BP (+1 mmHg)",
        "Ejection fraction (+1 percentage point)",
        "Diabetes: yes vs. no",
        "Smoker: yes vs. no",
        "Chronic kidney disease: yes vs. no",
        "NYHA class (+1 class)",
        "Beta-blocker: yes vs. no",
    ]

    figure, axis = plt.subplots(figsize=(12, 8))
    positions = np.arange(len(covariates))

    axis.errorbar(
        hazard_ratios,
        positions,
        xerr=[
            hazard_ratios - lower_limits,
            upper_limits - hazard_ratios,
        ],
        fmt="o",
        color="navy",
        ecolor="steelblue",
        capsize=4,
    )

    axis.axvline(1, color="gray", linestyle="--")
    axis.set_xscale("log")
    axis.set_yticks(positions)
    axis.set_yticklabels(labels)
    axis.invert_yaxis()
    axis.set_xlabel("Adjusted hazard ratio with 95% confidence interval")
    axis.set_title(
        "Cox Proportional Hazards: All-Cause Death Within 36 Months\n"
        f"n = {len(model_data)}, deaths = {int(model_data['death'].sum())}, "
        f"overall model p = {overall_test.p_value:.4g}"
    )
    axis.grid(axis="x", alpha=0.25)

    figure.text(
        0.5,
        0.02,
        "HR > 1 indicates higher death hazard; HR < 1 indicates lower hazard. "
        "Each estimate adjusts for all other listed covariates.",
        ha="center",
        fontsize=9,
    )
    figure.tight_layout(rect=(0, 0.06, 1, 1))

    output_path = OUTPUT_FOLDER / "cox_ph_heart_failure_survival.png"
    figure.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"\nSaved figure: {output_path}")

    plt.show()
    plt.close(figure)


def main():
    """Run and display both analyses."""
    run_logrank_analysis()
    run_cox_analysis()


if __name__ == "__main__":
    main()
