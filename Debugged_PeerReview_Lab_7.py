# Lab 7: Linear Regression
# Original scripts: Madison Lowenstein
# Revised by: Matt Picaroni
# Purpose: Load a selected CSV, clean column names, prompt for data ranges and variables,
# calculate OLS, and optionally save scatterplots with custom filenames, colors, and line widths.

from pathlib import Path
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from matplotlib.colors import is_color_like

LAB_DIR = Path(__file__).resolve().parent
FIGURES_DIR = LAB_DIR / "figures"


# Convert column names to snake_case.
def to_snake_case(column_name):
    text = str(column_name).strip()
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", text)
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text)
    text = re.sub(r"[^A-Za-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_").lower()


# Prompt for a CSV, load it, and list cleaned column names.
def load_dataset():
    while True:
        entered = input(
            "Enter a CSV filename or full path: "
        ).strip().strip('"')

        if not entered:
            print("Please enter a CSV filename.")
            continue

        path = Path(entered).expanduser()

        if not path.is_absolute():
            path = LAB_DIR / path

        try:
            df = pd.read_csv(path)
        except (OSError, ValueError, pd.errors.ParserError) as error:
            print(f"Could not load dataset: {error}")
            continue

        cleaned = [to_snake_case(column) for column in df.columns]

        if len(set(cleaned)) != len(cleaned) or "" in cleaned:
            print(
                "Column cleaning produced duplicate or empty names. "
                "Choose a corrected CSV."
            )
            continue

        df.columns = cleaned

        print(f"\nLoaded {len(df):,} rows from {path.name}.")
        print("\nAvailable column names:")

        for column in df.columns:
            print(column)

        return df


# Prompt for the user's choice of X or Y column.
def prompt_column(df, label):
    while True:
        entered = input(f"\nEnter the {label} column name: ")
        column = to_snake_case(entered)

        if column in df.columns:
            return column

        print("Column not found. Choose a name from the list above.")


# Keep rows with complete numeric values for both selected variables.
def prepare_data(df, x_col, y_col):
    if x_col == y_col:
        raise ValueError("Choose different X and Y variables.")

    data = df[[x_col, y_col]].copy()

    for column in [x_col, y_col]:
        # Remove thousands separators from values such as population counts.
        values = data[column].astype(str).str.replace(
            ",", "", regex=False
        )
        data[column] = pd.to_numeric(values, errors="coerce")

    data = data.replace([np.inf, -np.inf], np.nan)
    data = data.dropna(subset=[x_col, y_col])

    if len(data) < 2:
        raise ValueError(
            "OLS requires at least two complete numeric rows."
        )

    if data[x_col].nunique() < 2:
        raise ValueError(
            "X must contain at least two distinct values."
        )

    removed = len(df) - len(data)
    print(
        f"\nUsing {len(data):,} rows; "
        f"removed {removed:,} unusable rows."
    )

    return data


# Ask whether to save a plot with a custom filename.
def ask_to_save(fig, description):
    while True:
        answer = input(
            f"\nSave {description}? (Y/N): "
        ).strip().lower()

        if answer in ("n", "no"):
            return

        if answer not in ("y", "yes"):
            print("Enter Y or N.")
            continue

        while True:
            filename = input(
                "Enter a custom PNG filename or path relative to figures: "
            ).strip().strip('"')

            if not filename:
                print("Enter a filename.")
                continue

            try:
                output = Path(filename).expanduser()

                if output.suffix.lower() != ".png":
                    output = output.with_suffix(".png")

                if not output.is_absolute():
                    output = FIGURES_DIR / output

                if output.exists():
                    overwrite = input(
                        "File exists. Overwrite? (Y/N): "
                    ).strip().lower()

                    if overwrite not in ("y", "yes"):
                        continue

                output.parent.mkdir(parents=True, exist_ok=True)
                fig.savefig(
                    output,
                    dpi=300,
                    bbox_inches="tight",
                )

            except (OSError, ValueError) as error:
                print(f"Could not save figure: {error}")
                continue

            print(f"Saved figure to {output.resolve()}")
            return


# Create a scatterplot of the selected variables.
def create_scatterplot(data, x_col, y_col, formatting):
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.scatter(
        data[x_col],
        data[y_col],
        color=formatting["point_color"],
        alpha=0.6,
        edgecolor="k",
        linewidth=0.3,
    )

    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)

    title= formatting["title"] or f"{y_col} vs {x_col}"
    ax.set_title(f"{title} (n = {len(data)})")

    if formatting["grid"]:
        ax.grid(True, alpha=0.3)

    else:
        ax.grid(False)

    fig.tight_layout()
    return fig, ax

#Prompt for a custom number, with an optional default setting
def prompt_number(message, default=None):
    while True:
        entered = input(message).strip()

        if not entered:
            return default

        try:
            value = float(entered)

            if np.isfinite(value):
                return value

        except ValueError:
            pass

        print("Enter a valid number.")

# Filters both variables using inclusive limits
def select_data_ranges(data, x_col, y_col):
    print("\nSelect data ranges. Press Enter to leave a limit unrestricted.")
    print("Enter limits in the units stored in the CSV.")

    while True:
        filtered = data.copy()

        for column in (x_col, y_col):
            print(
                f"\n{column}: observed range "
                f"{data[column].min():.2f} to {data[column].max():.2f}"
            )

            while True:
                lower = prompt_number(f"Minimum {column}: ")
                upper =prompt_number(f"Maximum {column}: ")

                if lower is None or upper is None or lower <= upper:
                    break

                print("Minimum cannot exceed maximum. Try again.")

            if lower is not None:
                filtered = filtered[filtered[column] >= lower]

            if upper is not None:
                filtered = filtered[filtered[column] <= upper]

        # Require enough observation for regression with degrees of freedom
        if len(filtered) < 3:
            print("Fewer than three rows remain. Choose wider range. ")
        elif filtered[x_col].nunique() < 2:
            print("X must have at least 2 unique values.")
        else:
            print(f"\nUsing {len(filtered):,} rows within the selected range.")
            return filtered

# Validate a Matplotlib color.
def prompt_color(message, default):
    while True:
        color = input(message).strip() or default

        if is_color_like(color):
            return color

        print("Enter a valid color.")

#Collecting formating choices for both plots.
def prompt_plot_format():
    print("\nPlot formatting: press Enter to choose the default.")

    point_color = prompt_color("Point color [steelblue]: ", "steelblue")
    line_color = prompt_color("Regression line color [crimson]: ", "crimson")

    while True:
        line_width = prompt_number("Regression line width [2]: ", default=2)

        if line_width > 0:
            break

        print("Line width must be greater than zero.")
    while True:
        grid_choice = input("Show gridlines? [Y/N, default Y]: ").strip().lower()

        if grid_choice in ("", "y", "yes", "n", "no"):
            break

        print("Enter Y or N.")

    title = input("Custom plot title [automatic]: ").strip()

    return {"point_color": point_color,
            "line_width": line_width,
            "title": title,
            "grid": grid_choice in ("", "y", "yes"),
            "line_color": line_color,
        }



# Run the dataset selection, plotting, and regression workflow.
def main():
    print("Lab 7: Linear Regression")
    print(f"Default figure directory: {FIGURES_DIR}")

    df = load_dataset()

    while True:
        x_col = prompt_column(df, "X (independent variable)")
        y_col = prompt_column(df, "Y (dependent variable)")

        try:
            data = prepare_data(df, x_col, y_col)
        except ValueError as error:
            print(error)
            continue

        break

    data = select_data_ranges(data, x_col, y_col)
    formatting = prompt_plot_format()

    # Display and optionally save the scatterplot without an OLS line.
    fig, ax = create_scatterplot(data, x_col, y_col, formatting)

    print("\nClose the scatterplot preview to continue to the save prompt.")
    plt.show()
    ask_to_save(fig, "scatterplot without regression line")
    plt.close(fig)

    # Calculate the OLS regression with an intercept.
    X = sm.add_constant(data[x_col], has_constant="add")
    model = sm.OLS(data[y_col], X).fit()

    intercept = float(model.params["const"])
    slope = float(model.params[x_col])

    print("\nOLS results:")
    print(f"Independent variable: {x_col}")
    print(f"Dependent variable: {y_col}")
    print(f"Beta 0 (intercept): {intercept:.6f}")
    print(f"Beta 1 (slope): {slope:.10g}")
    print(f"R-squared: {model.rsquared:.6f}")
    print(
        f"Regression line: {y_col} = "
        f"{intercept:.6f} + ({slope:.10g}) * {x_col}"
    )

    # Recreate the scatterplot and add the fitted OLS line.
    fig, ax = create_scatterplot(data, x_col, y_col, formatting)

    x_line = np.linspace(
        data[x_col].min(),
        data[x_col].max(),
        100,
    )
    y_line = intercept + slope * x_line

    ax.plot(
        x_line,
        y_line,
        color=formatting["line_color"],
        linewidth=formatting["line_width"],
        label=f"OLS line (R² = {model.rsquared:.3f})",
    )

    title = formatting["title"] or f"{y_col} vs {x_col}"
    ax.set_title(f"{title} with OLS line (n= {len(data)})")

    ax.legend()
    fig.tight_layout()

    print("\nClose the OLS plot preview to continue to the save prompt.")
    plt.show()
    ask_to_save(fig, "scatterplot with OLS regression line")
    plt.close(fig)


if __name__ == "__main__":
    main()
