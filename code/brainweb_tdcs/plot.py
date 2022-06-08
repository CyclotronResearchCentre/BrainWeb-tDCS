from typing import Iterable, Optional, Union, List, Tuple

import arviz as az
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import HTML, display

from . import RegionOfInterest, Experiment


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


def plot_density(
    ax: plt.Axes, data: pd.Series, experiment: Experiment, x_label: str, title: str
) -> None:
    density = data.plot(kind="density", ax=ax)
    curve = density.get_children()[0]
    curve.set_linewidth(0)
    x, y = curve.get_data()
    area = ax.fill_between(x, 0, y, color=experiment.roi.color, lw=0)
    if not experiment.is_bipolar:
        plt.rcParams["hatch.linewidth"] = 4
        area.set_hatch("//")
        area.set_edgecolor(experiment.roi.hatch_color)
    # ax.hist(data, bins=100, density=True)
    ax.set_xlim([np.min(data), np.max(data)])
    ax.set_xlabel(x_label)
    ax.set_ylim(ymin=0)
    ax.set_title(title)


def plot_violins(ax: plt.Axes, experiment: Union[Experiment, List[Experiment]], data) -> None:
    # Plot violins
    violins = ax.violinplot(data, vert=True, showmeans=False, showextrema=False)
    for i, violin in enumerate(violins["bodies"]):
        e = experiment if isinstance(experiment, Experiment) else experiment[i]
        violin.set_facecolor(e.roi.color)
        violin.set_alpha(1)
        if not e.is_bipolar:
            plt.rcParams["hatch.linewidth"] = 4
            violin.set_hatch("//")
            violin.set_edgecolor(e.roi.hatch_color)
    # Plot extrema
    x = np.arange(1, len(data) + 1)
    ax.vlines(x, np.min(data, axis=1), np.max(data, axis=1), colors="k", lw=1)
    # Plot median and quantiles
    q1 = np.quantile(data, 0.25, axis=1)
    q3 = np.quantile(data, 0.75, axis=1)
    ax.vlines(x, q1, q3, colors="k", lw=3)
    means = np.mean(data, axis=1)
    ax.plot(x, means, "ko", markerfacecolor="white")
    return violins


def plot_bipolar_unipolar(
    ax: plt.Axes,
    voi: str,
    experiment: Experiment,
    data: pd.DataFrame,
    y_label: str,
    title: str,
) -> None:
    # Get data for each montage type
    data_per_montage = [
        data[voi][data["montage"] == m] for m in ("bipolar", "unipolar")
    ]
    # Plot violins
    violins = plot_violins(ax, experiment, data_per_montage)
    violin = violins["bodies"][1]
    plt.rcParams["hatch.linewidth"] = 4
    violin.set_hatch("//")
    violin.set_edgecolor(experiment.roi.hatch_color)
    # Annotate
    ax.set_xticks([1, 2])
    ax.set_xticklabels(["bipolar", "unipolar"])
    ax.set_ylabel(y_label)
    ax.set_title(title)


def plot_placement(
    ax: plt.Axes,
    voi: str,
    direction: str,
    experiment: Experiment,
    data: pd.DataFrame,
    y_label: str,
    title: str,
) -> None:
    # Get data for each montage type
    data_per_placement = [data[voi][data[direction] == p] for p in (-1, 0, 1)]
    # Plot violins
    plot_violins(ax, experiment, data_per_placement)
    # Annotate
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels([-1, 0, 1])
    ax.set_xlabel(f"${direction}$ (cm)")
    ax.set_ylabel(y_label)
    ax.set_title(title)


def plot_placement_categorical(
    ax: plt.Axes,
    voi: str,
    experiment: Experiment,
    data: pd.DataFrame,
    y_label: str,
    title: str,
) -> None:
    # Get data for each montage type
    placements = data["p"].unique()
    data_per_placement = [data[voi][data["p"] == p] for p in placements]
    # Plot violins
    plot_violins(ax, experiment, data_per_placement)
    # Annotate
    ax.set_xticks(np.arange(1, len(placements) + 1))
    ax.set_xticklabels(placements)
    ax.set_ylabel(y_label)
    ax.set_title(title)


def plot_conductivity_categorical(
    ax: plt.Axes,
    voi: str,
    experiment: Experiment,
    data: pd.DataFrame,
    y_label: str,
    title: str,
    use_latex=False,
) -> None:
    # Get data for each montage type
    profiles = data["k"].unique()
    data_per_placement = [data[voi][data["k"] == k] for k in profiles]
    # Plot violins
    plot_violins(ax, experiment, data_per_placement)
    # Annotate
    ax.set_xticks(np.arange(1, len(profiles) + 1))
    if use_latex:
        ax.set_xticklabels(["reference", *[f"halton$_{{ {i + 1} }}$" for i in range(20)]], rotation=90)
    else:
        ax.set_xticklabels(profiles, rotation=90)
    ax.set_ylabel(y_label)
    ax.set_title(title)


def plot_subject(
    ax: plt.Axes, voi: str, experiment: Experiment, data: pd.DataFrame, y_label: str, title: str
) -> None:
    # Get data for each montage type
    subjects = data["sub"].unique()
    data_per_subject = [data[voi][data["sub"] == s] for s in subjects]
    # Plot violins
    plot_violins(ax, experiment, data_per_subject)
    # Annotate
    ax.set_xticks(np.arange(1, len(subjects) + 1))
    ax.set_xticklabels([f"sub-{s:02d}" for s in subjects], rotation=90)
    ax.set_ylabel(y_label)
    ax.set_title(title)


def plot_posterior(
    ax: plt.Axes,
    experiment: Experiment,
    trace: az.InferenceData,
    summary: pd.DataFrame,
    param: str,
    x_label: str,
    title: str,
    category_id: int = 0,
    summary_param: Optional[str] = None,
    show_zero: bool = False,
    beta_suffix: Optional[str] = None,
    rope_width: float = 0
) -> Tuple[float, float]:
    n = summary_param if summary_param is not None else param
    # Display ROPE
    if rope_width > 0:
        ax.axvspan(-rope_width, rope_width, alpha=0.1, color="k")
    # Get kde
    overall_x, overall_y = az.kde(
        trace.posterior[param].values[:, :, category_id], bw_fct=2.5
    )
    # Plot credible interval
    s_min, s_max = summary[["2.5%", "97.5%"]].loc[n]
    idx = np.where(np.bitwise_and(overall_x >= s_min, overall_x <= s_max))[0]
    area = ax.fill_between(
        overall_x[idx],
        overall_y[idx],
        np.zeros(idx.size),
        color=experiment.roi.color,
        alpha=1,
        lw=0,
    )
    if not experiment.is_bipolar:
        plt.rcParams["hatch.linewidth"] = 4
        area.set_hatch("//")
        area.set_edgecolor(experiment.roi.hatch_color)
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
    # Compute HDI vs ROPE
    hdi, rope = (s_min, s_max), (-rope_width, rope_width)
    if rope[0] > hdi[1] or rope[1] < hdi[0]:
        return 0.0, 0.0
    inter = (max(hdi[0], rope[0]), min(hdi[1], rope[1]))
    dinter = abs(inter[1] - inter[0])
    return dinter / abs(hdi[1] - hdi[0]) * 100, dinter / abs(rope[1] - rope[0]) * 100