import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib import rcParams

from src.annotations import annots

# Use Systrom's matplotlib style
try:
    plt.style.use(
        "https://raw.githubusercontent.com/k-sys/covid-19/master/matplotlibrc"
    )
except Exception as e:
    print(e.message)

rcParams["font.family"] = "Helvetica"
current_date = datetime.date.today().strftime("%d %B %Y")


def original_smoothed(
    original: pd.DataFrame, smoothed: pd.DataFrame, current_date: str = current_date
) -> None:
    """
    Plot original and smoothed new cases
    """

    # Create figure with axes
    fig, ax = plt.subplots(figsize=(16, 8))

    # Plot original new cases
    original.cases.plot(
        c="k", alpha=0.5, linestyle=":", label="Actual", legend=True, ax=ax
    )

    # Plot smoothed new cases
    smoothed.cases.plot(c="k", label="Smoothed", legend=True, ax=ax)

    # Set title
    ax.set_title(
        f"Positive COVID-19 tests - last updated on {current_date}", fontsize=18
    )
    plt.xticks(ha="center")

    # Set label and ticks
    ax.set_ylabel("New Cases", fontsize=16)
    ax.set_xlabel("")

    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.xaxis.set_minor_locator(mdates.MonthLocator())
    ax.tick_params(axis="both", which="major", labelsize=14, rotation="default")

    # Remove frame legend
    ax.legend(frameon=False)

    # Remove spines
    sns.despine()

    # Save figure
    fig.tight_layout()
    fig.savefig("figures/original_smoothed.svg")


def plot_rt(
    df: pd.DataFrame,
    smooth: bool = True,
    annotate: bool = False,
    current_date: str = current_date,
) -> None:
    """
    Plot most likely Rt and HDI
    """

    # Logic to apply smoothing
    if smooth:
        df = (
            df.rolling(14, win_type="gaussian", min_periods=1, center=True)
            .mean(std=2)
            .round(2)
        )

    # Create figure with axes
    fig, ax = plt.subplots(figsize=(16, 8))

    # Plot R=1
    ax.axhline(y=1, c="red", linestyle=":", linewidth=2)

    # Plot most likely Rt
    df.most_likely.plot(
        c="k",
        label="Most Likely $R_t$",
        linewidth=1,
        # marker="o",
        markevery=2,
        markersize=5,
        markerfacecolor="white",
    )

    # Plot 95% CI
    ax.fill_between(
        x=df.index, y1=df.low_95, y2=df.high_95, color="#e6e6e6", label="95% CI"
    )

    # Plot 90% CI
    ax.fill_between(
        x=df.index, y1=df.low_65, y2=df.high_65, color="#c8c8c8", label="65% CI"
    )

    # Set title
    ax.set_title(
        f"Last updated on {current_date} with $R_t = {df.most_likely.iloc[-1]}$ and 95% confidence in range ${df.low_95.iloc[-1]} - {df.high_95.iloc[-1]}$",
        fontsize=18,
    )

    # Plot annotations
    if annotate:
        for date in annots.keys():
            ax.annotate(
                annots[date]["text"],
                xy=(annots[date]["date"], df.loc[date].most_likely),
                xytext=(
                    annots[date]["xytext"][0],
                    df.loc[date].most_likely + annots[date]["xytext"][1],
                ),
                arrowprops=dict(
                    facecolor="#333",
                    edgecolor="#333",
                    shrink=0.1,
                    width=0.5,
                    headwidth=6,
                ),
            )

    # Set label and ticks
    ax.set_ylabel("$R_{t}$", fontsize=16)
    ax.set_xlabel("")

    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

    ax.set_yticks(range(4))
    ax.set_ylim(-0.1, 4)
    ax.set_xlim(df.index[0], df.index[-1])
    ax.tick_params(axis="both", which="major", labelsize=14, rotation="default")
    plt.xticks(ha="center")

    # Remove frame legend
    ax.legend(frameon=False, fontsize=16)

    # Remove spines
    sns.despine()

    # Save figure
    fig.tight_layout()
    fig.savefig("figures/most_likely_rt.svg")
