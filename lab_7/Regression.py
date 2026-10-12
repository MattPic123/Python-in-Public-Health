#-----------------------------------
# Linear Regression Lab
# Name: Matt Picaroni
# Purpose: Loading CSV, cleaning column names to snake_case, create scatterplot,/
#\ Calculate OLS regression, and optionally save both plots
#-----------------------------------

from __future__ import annotations

#import helpers
import re
from difflib import get_close_matches
from pathlib import Path

#Loading Libraries
try:
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
except ImportError as error:
    raise SystemExit(f"Error while importing modules: {error}") from error

# storing project and figure locations
LAB_DIR = Path(__file__).resolve().parent
FIGURES_DIR = LAB_DIR / "figures"

# clean up column-names
def to_snake_case(column_name: object) -> str:
    """ Converts a column name to snake case """
    text = str(column_name).strip()
    text = re.sub(r"([a-z0-9])(A-Z])", r"\1_\2", text)
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", text)
    text = re.sub(r"[^A-Za-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_").lower()


# Dataset selection and loading
def prompt_dataset() -> Path:
    """ Ask for a CSV filename or path and return its resolved path"""
    while True:
        entered_path = input(
            "Enter a CSV filename or path: "
        ).strip().strip('"')
        if not entered_path:
            print("Enter a CSV filename or path")
            continue
        candidate = Path(entered_path).expanduser()
        if not candidate.is_absolute():
            candidate = LAB_DIR / candidate

        if candidate.is_file():
            return candidate.resolve()

        print(f"Could not find: {candidate}")

def load_dataset(dataset_path: Path) -> pd.DataFrame:
    """ Loads a CSV dataset and normalize column names """
    try:
        data = pd.read_csv(dataset_path)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as error:
        raise ValueError(f"Could not load dataset: {error}") from error

    cleaned_names = [to_snake_case(name) for name in data.columns]

    if len(set(cleaned_names)) != len(cleaned_names):
        duplicates = sorted(
            name for name in set(cleaned_names)
            if cleaned_names.count(name) > 1
        )
        raise ValueError(
            "Cleaning the column names created duplicate names: "
            + ", ".join(duplicates)
        )
    data.columns = cleaned_names
    return data

# Independent and dependent variable selection
def prompt_column(data: pd.DataFrame, variable_label: str) -> str:
    """ Prompts the user to enter a column name """
    avalable_columns = list(data.columns)

    print("\nAvailable column names:")
    for number, column in enumerate(avalable_columns, start=1):
        print(f" {number}. {column}")

    while True:
        entered_name = input(
            f"Enter the {variable_label} column name: "
        ).strip()

        if entered_name in data.columns:
            return entered_name

        normalized_name = to_snake_case(entered_name)
        if normalized_name in data.columns:
            return normalized_name

        suggestions = get_close_matches(
            normalized_name,
            avalable_columns,
            n=3,
            cutoff=0.70,
        )
        if suggestions:
            print(
                "No exact match. Closest available column name(s): "
                + ", ".join(suggestions)
            )
        print("That column was not found. Choose a name from the list above.")

        #Removing rows missing either selected regression value
def prepare_regression_data(
    data: pd.DataFrame,
    x_name: str,
    y_name: str,
) -> tuple[pd.Series, pd.Series]:
    """ Keep rows with numeric, non-missing values for both variables"""
    selected = data[[x_name, y_name]].copy()
    selected[x_name] = pd.to_numeric(selected[x_name], errors="coerce")
    selected[y_name] = pd.to_numeric(selected[y_name], errors="coerce")
    selected = selected.replace([np.inf, -np.inf], np.nan)
    selected = selected.dropna(subset=[x_name, y_name])

    if selected.empty:
        raise ValueError("Could not find any usable values for both variables")

    if len(selected) <2:
        raise ValueError("At least two complete numeric rows are required for OLS")

    if selected[x_name].nunique() < 2:
        raise ValueError("The X variable must contain two distinct values")

    return selected[x_name], selected[y_name]

# OLS Calculation
def calculate_ols(
    x: pd.Series,
    y: pd.Series,
) -> tuple[float, float, float]:
    """ Return OLS intercept, slope, and R-squared for y = intercept = slope*x."""
    x_values = x.to_numpy(dtype=float)
    y_values = y.to_numpy(dtype=float)

    design_matrix = np.column_stack(
        (np.ones(len(x_values)), x_values)
    )

    intercept, slope = np.linalg.lstsq(
        design_matrix,
        y_values,
        rcond=None,
    )[0]

    predicted = intercept + slope * x_values
    residual_sum_squares = float(
        np.sum((y_values - predicted) ** 2)
    )
    total_sum_squares = float(
        np.sum((y_values - np.mean(y_values)) ** 2)
    )

    if total_sum_squares == 0:
        r_squared = float("nan")
    else:
        r_squared = 1 - residual_sum_squares/total_sum_squares

    return float(intercept), float(slope), float(r_squared)

# custom figure filenames and save prompts
def make_output_path(file_name: str) -> Path:
    """Resolve users figure name under the figures folder by default"""
    output_path = Path(file_name.strip().strip('"')).expanduser()

    if output_path.suffix.lower() != ".png":
        output_path = output_path.with_suffix(".png")

    if not output_path.is_absolute():
        output_path = FIGURES_DIR / output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path.resolve()

def ask_to_save(figure: plt.Figure, description: str) -> None:
    """Offer to save the figure under a custom name"""
    while True:
        response = input(
            f"Would you like to save the {description}? (Y/N): "
        ).strip().lower()

        if response in ["y", "yes"]:
            while True:
                file_name = input(
                    "Enter a custom png filename or path: "
                ).strip()

                if file_name:
                    output_path = make_output_path(file_name)
                    figure.savefig(
                        output_path,
                        dpi=300,
                        bbox_inches="tight",
                    )
                    print(f"Saved figure to: {output_path}")
                    return

                print("Enter a filename.")
        elif response in ["n", "no"]:
            return

        else:
            print("Enter a valid choice.")

#scatterplot without a regression line
def plot_scatter(
    x: pd.Series,
    y: pd.Series,
    x_name: str,
    y_name: str,
) -> plt.Figure:
    figure, axis = plt.subplots(figsize=(8, 6))
    axis.scatter(
        x,
        y,
        alpha=0.75,
        edgecolor="white",
        linewidth=0.4,
)
    axis.set_xlabel(x_name)
    axis.set_ylabel(y_name)
    axis.set_title(f"{y_name} vs {x_name}")
    axis.grid(True, alpha=0.25)
    figure.tight_layout()
    return figure

# scatterplot with the fitted OLS regression line
def plot_regression(
    x: pd.Series,
    y: pd.Series,
    x_name: str,
    y_name: str,
    intercept: float,
    slope: float,
) -> plt.Figure:
    figure, axis = plt.subplots(figsize=(8, 6))
    axis.scatter(
    x,
    y,
    alpha = 0.75,
    edgecolor = "white",
    linewidth = 0.4,
    label="Observed",
    )
    line_x = np.linspace(float(x.min()), float(x.max()), 200)
    axis.plot(
        line_x,
        intercept + slope * line_x,
        color="black",
        linewidth= 2,
        label="OLS regression line",
    )
    axis.set_xlabel(x_name)
    axis.set_ylabel(y_name)
    axis.set_title(f"{y_name} vs {x_name} with OLS line")
    axis.grid(True, alpha=0.25)
    axis.legend(frameon=False)
    figure.tight_layout()
    return figure

# Main Program
def main() -> None:
    """ Run the dataset, plotting, and OLS workflow"""
    print("Linear Regression Lab")
    print(f"Figures will be saved to: {FIGURES_DIR}")

    # Loading selected dataset and asking for x and y columns
    dataset_path = prompt_dataset()

    try:
        data = load_dataset(dataset_path)
    except ValueError as error:
        print(error)
        return
    print(f"\nLoaded {len(data):,} rows from {dataset_path.name}.")

    x_name = prompt_column(
        data,
        "X (independent variable)",
    )
    y_name = prompt_column(
        data,
        "Y (dependent variable)",
    )

    # Keep only complete numeric observations for the selected variables.
    try:
        x, y = prepare_regression_data(data, x_name, y_name)
    except ValueError as error:
        print(error)
        return
    removed_rows = len(data) - len(x)
    print(
        f"\nUsing {len(x):,} complete numeric rows; "
        f"{removed_rows:,} row(s)."
    )
    # Display and optionally save scatterplot without OLS line.
    scatter_figure = plot_scatter(x, y, x_name, y_name)
    plt.show()
    ask_to_save(scatter_figure, "Scatterplot without regression line",
    )
    plt.close(scatter_figure)

    # calculate and report OLS results before displaying
    intercept, slope, r_square = calculate_ols(x, y)

    print("\nOLS results:")
    print(f" Intercept: {intercept:.6f}")
    print(f" Slope: {slope:.6f}")
    print(f" R-squared: {r_square:.6f}")
    print(
        f" Regression line: "
        f"{y_name} = {intercept:.6f} +- {slope:.6f} * {x_name}"
    )

    regression_figure = plot_regression(x, y, x_name, y_name, intercept, slope,
    )
    plt.show()
    ask_to_save(regression_figure, "Regression line")
    plt.close(regression_figure)

    # Run workflow only when this file is executed directly.

if __name__ == "__main__":
    main()
