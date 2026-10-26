"""
Matt Picaroni
Week 9 Logistic and Poisson Regression
Prompts for a CSV dataset, cleans column names, fits a model,
and optionally saves the results to a custom text file.
"""


# Section 1: Import required libraries

import re
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from statsmodels.stats.outliers_influence import (
    variance_inflation_factor,
)


# Section 2: Convert column names to snake_case

def to_snake_case(column_name):
    """Convert a column name to snake_case."""
    text = str(column_name).strip()
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", text)
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text)
    text = re.sub(r"[^A-Za-z0-9]+", "_", text)
    return text.strip("_").lower()


# Section 3: Prompt for and load the dataset

def load_dataset():
    """Prompt until a CSV dataset loads successfully."""
    while True:
        filename = input("\nEnter the CSV filename or full path: ")
        path = Path(filename.strip().strip('"').strip("'")).expanduser()

        try:
            df = pd.read_csv(path)
            df.columns = [to_snake_case(col) for col in df.columns]

            if df.columns.duplicated().any():
                raise ValueError(
                    "Some column names are duplicates after cleaning."
                )

            # Display the cleaned column names.
            print(f"\nLoaded {len(df)} rows.")
            print("\nAvailable columns:")
            print("\n".join(df.columns))

            return df, path

        except (OSError, ValueError, pd.errors.ParserError) as error:
            print(f"Could not load the dataset: {error}")


# Section 4: Select predictors and the response variable

def select_columns(df):
    """Select multiple predictors and one response."""
    while True:
        entered = input(
            "\nEnter predictor columns separated by commas: "
        )

        # Remove repeated predictors while preserving their order.
        predictors = list(
            dict.fromkeys(
                to_snake_case(col)
                for col in entered.split(",")
                if col.strip()
            )
        )

        response = to_snake_case(
            input("Enter the response column: ")
        )

        # Check that all selected columns exist.
        missing = [
            col for col in predictors + [response]
            if col not in df.columns
        ]

        if not predictors:
            print("Enter at least one predictor.")
        elif missing:
            print(f"Columns not found: {', '.join(missing)}")
        elif response in predictors:
            print("The response cannot also be a predictor.")
        else:
            return predictors, response


# Section 5: Clean selected data and remove missing values

def prepare_data(df, predictors, response):
    """Convert selected columns to numbers and remove incomplete rows."""
    data = df[predictors + [response]].copy()

    for column in data.columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.replace([np.inf, -np.inf], np.nan).dropna()

    if len(data) <= len(predictors) + 1:
        raise ValueError("Too few complete rows for this model.")

    # Check for predictors that have only one value.
    constant_columns = [
        col for col in predictors if data[col].nunique() < 2
    ]

    if constant_columns:
        raise ValueError(
            f"Predictors have no variation: {constant_columns}"
        )

    # Add an intercept to the predictor matrix.
    X = sm.add_constant(data[predictors], has_constant="add")
    y = data[response]

    # Check for perfectly redundant predictors.
    if np.linalg.matrix_rank(X.to_numpy()) < X.shape[1]:
        raise ValueError(
            "Some predictors are perfectly collinear. "
            "Remove redundant predictors."
        )

    return data, X, y


# Section 6: Fit the logistic regression model

def logistic_regression(X, y):
    """Fit logistic regression and report classification performance."""

    # Confirm that the response contains both binary categories.
    if set(y.unique()) != {0, 1}:
        raise ValueError(
            "The logistic response must contain both 0 and 1."
        )

    model = sm.Logit(y, X).fit(disp=False, maxiter=200)

    if not model.mle_retvals.get("converged", False):
        raise ValueError("Logistic regression did not converge.")

    # Convert predicted probabilities to categories using 0.5.
    probabilities = model.predict(X)
    predictions = (probabilities >= 0.5).astype(int)

    # Section 6a: Create the confusion matrix

    matrix = pd.DataFrame(
        confusion_matrix(y, predictions, labels=[0, 1]),
        index=["Actual 0", "Actual 1"],
        columns=["Predicted 0", "Predicted 1"],
    )

    # Section 6b: Calculate precision and category support

    report = classification_report(
        y,
        predictions,
        labels=[0, 1],
        output_dict=True,
        zero_division=0,
    )

    lowest_precision = min(
        report["0"]["precision"],
        report["1"]["precision"],
    )

    enough_support = all(
        report[label]["support"] >= 30
        for label in ["0", "1"]
    )

    # Section 6c: Compile logistic regression results

    output = [
        model.summary().as_text(),
        "\nCONFUSION MATRIX",
        matrix.to_string(),
        "\nCLASSIFICATION REPORT",
        classification_report(
            y,
            predictions,
            labels=[0, 1],
            digits=4,
            zero_division=0,
        ),
        f"Accuracy: {accuracy_score(y, predictions):.4%}",
        f"Lowest class precision: {lowest_precision:.4f}",
        f"Both categories have at least 30 support: {enough_support}",
        f"McFadden pseudo-R-squared: {model.prsquared:.6f}",
        "\nEvaluation uses the same rows used to fit the model.",
        "These are training results, not test-set performance.",
        "Pseudo-R-squared is not the percentage of variance explained.",
    ]

    return "\n".join(output)


# Section 7: Fit the poisson regression model

def poisson_regression(X, y):
    """Fit Poisson regression and calculate predictor VIF values."""

    # Check that the response is nonnegative and has variation.
    if (y < 0).any():
        raise ValueError("The Poisson response cannot be negative.")

    if y.nunique() < 2:
        raise ValueError("The response must have variation.")

    note = ""

    # Warn before using noninteger values for the assignment.
    if not np.allclose(y, np.round(y), rtol=0, atol=1e-9):
        print(
            "\nWARNING: The response contains noninteger values."
            "\nPoisson count regression requires nonnegative counts."
            "\nPrevalence percentages are not counts."
        )

        proceed = input(
            "Continue only as an assignment demonstration? (y/n): "
        ).strip().lower()

        if proceed not in {"y", "yes"}:
            raise ValueError(
                "Poisson cancelled. Select an actual count response."
            )

        note = (
            "ASSIGNMENT DEMONSTRATION: The response is noninteger. "
            "The Poisson count assumption is not satisfied. "
            "Values were not rounded or converted to counts.\n\n"
        )

    model = sm.GLM(
        y,
        X,
        family=sm.families.Poisson(),
    ).fit(maxiter=200)

    if not model.converged:
        raise ValueError("Poisson regression did not converge.")

    # Section 7a: Calculate variance inflation factors

    # Include the intercept in calculations, but report predictors only.
    vif = pd.DataFrame(
        {
            "predictor": X.columns[1:],
            "VIF": [
                variance_inflation_factor(X.to_numpy(), index)
                for index in range(1, X.shape[1])
            ],
        }
    )

    # Section 7b: Identify statistically significant predictors

    coefficients = pd.DataFrame(
        {
            "coef": model.params,
            "p_value": model.pvalues,
            "exp_coef": np.exp(model.params),
        }
    ).drop(index="const")

    significant = coefficients[
        coefficients["p_value"] < 0.05
    ]

    significant_vif = vif[
        vif["predictor"].isin(significant.index)
    ]

    # Section 7c: Calculate model fit statistics

    pseudo_r2 = 1 - model.llf / model.llnull
    dispersion = model.pearson_chi2 / model.df_resid

    # Section 7d: Compile poisson regression results

    output = [
        note + model.summary().as_text(),
        "\nPREDICTOR VIF",
        vif.to_string(index=False),
        "\nSIGNIFICANT PREDICTORS AT P < 0.05",
        significant.to_string(),
        f"\nNumber of significant predictors: {len(significant)}",
        "\nVIF FOR SIGNIFICANT PREDICTORS",
        significant_vif.to_string(index=False),
        f"\nMcFadden pseudo-R-squared: {pseudo_r2:.6f}",
        f"Pearson dispersion statistic: {dispersion:.6f}",
        "\nPseudo-R-squared is not the percentage of variance explained.",
    ]

    if not significant.empty:
        largest_effect = significant["coef"].abs().idxmax()
        smallest_p = significant["p_value"].idxmin()

        output.extend(
            [
                f"Largest absolute significant coefficient: {largest_effect}",
                f"Smallest predictor p-value: {smallest_p}",
                "Coefficient magnitude describes effect size on the log scale.",
                "Statistical significance is assessed using p-values.",
            ]
        )

    return "\n".join(output)


# Section 8: Save output to a custom text file

def save_output(output):
    """Optionally save results with a custom filename."""
    choice = input("\nSave the output to a .txt file? (y/n): ")

    if choice.strip().lower() not in {"y", "yes"}:
        return

    while True:
        filename = input("Enter an output filename or path: ").strip()
        filename = filename.strip('"').strip("'")

        if not filename:
            print("Enter a filename.")
            continue

        path = Path(filename).expanduser().with_suffix(".txt")

        # Confirm before replacing an existing file.
        if path.exists():
            overwrite = input(
                f"{path} already exists. Overwrite? (y/n): "
            )
            if overwrite.strip().lower() not in {"y", "yes"}:
                continue

        try:
            path.write_text(output, encoding="utf-8")
            print(f"Saved to: {path.resolve()}")
            return
        except OSError as error:
            print(f"Could not save the output: {error}")


# Section 9: Control the program and display results

def main():
    """Run the interactive regression program."""
    while True:
        try:
            df, path = load_dataset()

            # Ask which regression model to run.
            while True:
                model_type = input(
                    "\nChoose logistic or poisson: "
                ).strip().lower()

                if model_type in {"logistic", "poisson"}:
                    break

                print("Enter logistic or poisson.")

            predictors, response = select_columns(df)
            data, X, y = prepare_data(df, predictors, response)

            # Record the selected variables and row counts.
            details = (
                f"Dataset: {path.name}\n"
                f"Model: {model_type}\n"
                f"Predictors: {', '.join(predictors)}\n"
                f"Response: {response}\n"
                f"Original rows: {len(df)}\n"
                f"Rows used: {len(data)}\n"
                f"Rows removed: {len(df) - len(data)}\n\n"
            )

            # Run the selected regression.
            if model_type == "logistic":
                results = logistic_regression(X, y)
            else:
                results = poisson_regression(X, y)

            output = details + results
            print("\n" + output)
            save_output(output)

        except (ValueError, np.linalg.LinAlgError) as error:
            print(f"\nUnable to complete the regression: {error}")

        # Allow another dataset or model to be analyzed.
        again = input("\nRun another regression? (y/n): ")

        if again.strip().lower() not in {"y", "yes"}:
            break


# Section 10: Start the program

if __name__ == "__main__":
    main()