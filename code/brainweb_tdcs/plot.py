from typing import Iterable, Optional

import arviz as az
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import HTML, display

from . import RegionOfInterest


def display_side_by_side(dfs: Iterable[pd.DataFrame], captions: Iterable[str]) -> None:
    # https://stackoverflow.com/a/57832026
    output = ""
    for caption, df in zip(captions, dfs):
        output += (
            df.style.set_table_attributes("style='display: inline'")
            .set_caption(caption)
            .format(precision=3)
            ._repr_html_()
        )
        output += "\xa0\xa0\xa0"
    display(HTML(output))


def plot_violins(ax: plt.Axes, data) -> None:
    # Plot violins
    violins = ax.violinplot(data, vert=True, showmeans=False, showextrema=False)
    for violin in violins["bodies"]:
        violin.set_facecolor("k")
        violin.set_alpha(0.1)
    # Plot extrema
    x = np.arange(1, len(data) + 1)
    ax.vlines(x, np.min(data, axis=1), np.max(data, axis=1), colors="k", lw=1)
    # Plot median and quantiles
    q1 = np.quantile(data, 0.25, axis=1)
    q3 = np.quantile(data, 0.75, axis=1)
    ax.vlines(x, q1, q3, colors="k", lw=3)
    means = np.mean(data, axis=1)
    ax.plot(x, means, "ko", markerfacecolor="white")


def plot_bipolar_unipolar(
    ax: plt.Axes, voi: str, data: pd.DataFrame, y_label: str, title: str
) -> None:
    # Get data for each montage type
    data_per_montage = [
        data[voi][data["montage"] == m] for m in ("bipolar", "unipolar")
    ]
    # Plot violins
    plot_violins(ax, data_per_montage)
    # Annotate
    ax.set_xticks([1, 2])
    ax.set_xticklabels(["bipolar", "unipolar"])
    ax.set_ylabel(y_label)
    ax.set_title(title)


def plot_placement(
    ax: plt.Axes, voi: str, direction: str, data: pd.DataFrame, y_label: str, title: str
) -> None:
    # Get data for each montage type
    data_per_placement = [data[voi][data[direction] == p] for p in (-1, 0, 1)]
    # Plot violins
    plot_violins(ax, data_per_placement)
    # Annotate
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels([-1, 0, 1])
    ax.set_xlabel(f"${direction}$ (cm)")
    ax.set_ylabel(y_label)
    ax.set_title(title)


def plot_placement_categorical(
    ax: plt.Axes, voi: str, data: pd.DataFrame, y_label: str, title: str
) -> None:
    # Get data for each montage type
    placements = data["p"].unique()
    data_per_placement = [data[voi][data["p"] == p] for p in placements]
    # Plot violins
    plot_violins(ax, data_per_placement)
    # Annotate
    ax.set_xticks(np.arange(1, len(placements) + 1))
    ax.set_xticklabels(placements)
    ax.set_ylabel(y_label)
    ax.set_title(title)


def plot_conductivity_categorical(
    ax: plt.Axes, voi: str, data: pd.DataFrame, y_label: str, title: str
) -> None:
    # Get data for each montage type
    profiles = data["k"].unique()
    data_per_placement = [data[voi][data["k"] == k] for k in profiles]
    # Plot violins
    plot_violins(ax, data_per_placement)
    # Annotate
    ax.set_xticks(np.arange(1, len(profiles) + 1))
    ax.set_xticklabels(profiles, rotation=90)
    ax.set_ylabel(y_label)
    ax.set_title(title)


def plot_posterior(
    ax: plt.Axes,
    trace: az.InferenceData,
    summary: pd.DataFrame,
    param: str,
    x_label: str,
    title: str,
    category_id: int = 0,
    summary_param: Optional[str] = None,
    show_zero: bool = False,
    beta_suffix: Optional[str] = None,
) -> None:
    # Get kde
    overall_x, overall_y = az.kde(
        trace.posterior[param].values[:, :, category_id], bw_fct=2.5
    )
    # Plot credible interval
    n = summary_param if summary_param is not None else param
    s_min, s_max = summary[["2.5%", "97.5%"]].loc[n]
    idx = np.where(np.bitwise_and(overall_x >= s_min, overall_x <= s_max))[0]
    ax.fill_between(
        overall_x[idx], overall_y[idx], np.zeros(idx.size), color="k", alpha=0.1, lw=0
    )
    ax.vlines(
        overall_x[idx[0]], ymin=0, ymax=overall_y[idx[0]], color="k", linestyle="--"
    )
    ax.text(
        overall_x[idx[0]],
        overall_y[idx[0]] * 1.01,
        f"{summary['2.5%'].loc[n]:.2f}",
        ha="right",
        va="bottom",
    )
    ax.vlines(
        overall_x[idx[-1]], ymin=0, ymax=overall_y[idx[-1]], color="k", linestyle="--"
    )
    ax.text(
        overall_x[idx[-1]],
        overall_y[idx[-1]] * 1.01,
        f"{summary['97.5%'].loc[n]:.2f}",
        ha="left",
        va="bottom",
    )
    # Plot maximum likelihood
    max_idx = np.argmax(overall_y)
    ax.vlines(
        overall_x[max_idx],
        ymin=0,
        ymax=overall_y[max_idx],
        color="k",
        linestyle="-.",
        label="Max. likelihood",
    )
    ax.text(
        overall_x[max_idx],
        overall_y[max_idx] * 1.05,
        f" {overall_x[max_idx]:.2f}",
        ha="center",
        va="bottom",
    )
    # Plot posterior
    for chain in trace.posterior[param][:, :, category_id]:
        x, y = az.kde(chain, bw_fct=2.5)
        ax.plot(x, y, "--", lw=0.5, color="k", alpha=0.5)
    # Display zero
    if show_zero:
        ax.axvline(x=0, color="k", lw=0.5)
    ax.plot(overall_x, overall_y, "k-")
    # Annotate
    ax.set_xlabel(x_label)
    ax.set_ylabel(
        r"P($\beta$)" if beta_suffix is None else fr"P($\beta_{{{beta_suffix}}}$)"
    )
    ax.set_ylim([0, overall_y[max_idx] * 1.25])
    ax.set_title(title)
    ax.legend(loc=1)
