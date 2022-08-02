#!/usr/bin/env python3

from pathlib import Path
import sys

import chaospy as cp
import pandas as pd
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern

# Nextflow input parameters
ROI = "${roi}"
ANODE = "${anode}"
CATHODE = "${cathode}"
CSV_PATH = Path("${csv}")
BRAINWEB_TDCS_CODE_DIR = "${launchDir}/code"
sys.path.append(BRAINWEB_TDCS_CODE_DIR)

from brainweb_tdcs import TISSUES

RANDOM_SEED = 1234
VOIS = ["e", "e_r"]


def resize_pdf(tissue, pdf):
    return (pdf - tissue.k_norm.cdf(tissue.k_min)) / (
        tissue.k_norm.cdf(tissue.k_max) - tissue.k_norm.cdf(tissue.k_min)
    )


def get_weights(tissue, x):
    return resize_pdf(tissue, tissue.k_norm.pdf(x))


if __name__ == "__main__":
    # Load original data
    data = pd.read_csv(CSV_PATH, sep=";")
    # Compute standardized kappas
    k_names = ["k_wm", "k_gm", "k_csf", "k_skl", "k_sft"]
    kappa = data.drop_duplicates("k")[["k", *k_names]]
    new_kappa = kappa.copy()
    dist = cp.J(*[cp.Uniform(0, 1) for _ in range(len(TISSUES))])
    cdfs = dist.sample(20, rule="halton", seed=RANDOM_SEED)
    for name, cdf, tissue in zip(k_names, cdfs, TISSUES.values()):
        k = np.linspace(tissue.k_min, tissue.k_max, 1000000)
        dist_cdf = resize_pdf(tissue, tissue.k_norm.cdf(k))
        new_kappa[name] = np.hstack(
            (
                [new_kappa[name].values[0]],
                k[np.abs(cdf[:, np.newaxis] - dist_cdf[np.newaxis, :]).argmin(axis=1)],
            )
        )
    # Build training set
    n_sub, n_p = len(data["sub"].unique()), len(data["p"].unique())
    x_s = kappa[k_names].values
    y_s = {voi: np.zeros((len(kappa), n_sub * n_p)) for voi in VOIS}
    for voi in VOIS:
        for i, p in enumerate(data["p"].unique()):
            for j, sub in enumerate(data["sub"].unique()):
                col = i * n_sub + j
                y_s[voi][:, col] = data[(data["p"] == p) & (data["sub"] == sub)][voi]
    # Build GPR
    kernel = ConstantKernel() * Matern(length_scale=[1.0] * len(k_names), nu=2.5)
    gpr = {
        voi: GaussianProcessRegressor(
            kernel=kernel, n_restarts_optimizer=10, random_state=0, alpha=1e-10
        ).fit(x_s, y_s[voi])
        for voi in VOIS
    }
    # Generate new dataset
    y_gpr = {voi: gpr[voi].predict(new_kappa[k_names].values) for voi in VOIS}
    sub = np.repeat(data["sub"].unique(), n_p * len(new_kappa))
    new_data = pd.DataFrame(
        dict(
            sub=sub,
            k=data["k"].values.ravel(),
            k_id=data["k_id"].values.ravel(),
            **{
                k_name: np.tile(
                    np.repeat(new_kappa[k_names].values.ravel(), n_p), n_sub
                )
                for k_name in k_names
            },
            p=data["p"].values.ravel(),
            p_id=data["p_id"].values.ravel(),
        )
    )
    for voi, y in y_gpr.items():
        new_data[voi] = np.hstack(
            [y[:, i_sub::n_sub] for i_sub in range(n_sub)]
        ).ravel()
    new_data.to_csv(
        f"roi-{ROI}_anode-{ANODE}_cathode-{CATHODE}_gpr.csv", sep=";", index=False
    )
