import os
from dataclasses import dataclass, field
from email.policy import default
from pathlib import Path

import pandas as pd

from . import ROIS, MissingEnvironmentVariable, RegionOfInterest


@dataclass
class Experiment:

    roi: RegionOfInterest
    anode: str
    cathode: str
    is_bipolar: bool = field(default=True, repr=False)

    @property
    def montage(self) -> str:
        return f"{self.anode}-{self.cathode}"

    @property
    def data_file_name(self) -> str:
        return f"roi-{self.roi.name}_anode-{self.anode}_cathode-{self.cathode}.csv"

    @property
    def data_path(self) -> Path:
        try:
            data_dir = os.environ["BRAINWEB_TDCS_DATA_DIR"]
            return Path(data_dir) / "experiments" / self.data_file_name
        except KeyError:
            raise MissingEnvironmentVariable(
                "Missing 'BRAINWEB_TDCS_DATA_DIR' environment variable."
            )

    def get_data(self) -> pd.DataFrame:
        return pd.read_csv(self.data_path, sep=";")
    
    def get_gpr_data(self) -> pd.DataFrame:
        return pd.read_csv(str(self.data_path).replace(".csv", "_gpr.csv"), sep=";")


EXPERIMENTS = [
    Experiment(ROIS[0], "C3", "C4"),
    Experiment(ROIS[0], "C3", "Fp2", False),
    Experiment(ROIS[1], "F3", "F4"),
    Experiment(ROIS[1], "F3", "Fp2", False),
    Experiment(ROIS[2], "F7", "F8"),
    Experiment(ROIS[3], "P3", "P4"),
]
