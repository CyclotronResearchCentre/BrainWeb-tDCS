from . import EXPERIMENTS, Experiment, RegionOfInterest


def get_experiments_for_roi(roi: RegionOfInterest) -> Experiment:
    return [e for e in EXPERIMENTS if e.roi == roi]
