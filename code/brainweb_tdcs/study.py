import pymc3 as pm

from . import EXPERIMENTS, Experiment, RegionOfInterest


def get_experiments_for_roi(roi: RegionOfInterest) -> Experiment:
    return [e for e in EXPERIMENTS if e.roi == roi]


def log_marginal_likelihood(model, random_seed):
    with model.backend.model as m:
        return pm.sample_smc(
            1000, random_seed=random_seed
        ).report.log_marginal_likelihood