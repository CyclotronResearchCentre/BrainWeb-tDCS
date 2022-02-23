import os
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from . import MissingEnvironmentVariable


@dataclass
class RegionOfInterest:

    name: str
    long_name: str = ""
    color: str = "#000000"

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

    @property
    def data_file_name(self) -> str:
        return f"roi-{self.name}.csv"

    @property
    def data_path(self) -> Path:
        try:
            data_dir = os.environ["BRAINWEB_TDCS_DATA_DIR"]
            return Path(data_dir) / "rois" / self.data_file_name
        except KeyError:
            raise MissingEnvironmentVariable(
                "Missing 'BRAINWEB_TDCS_DATA_DIR' environment variable."
            )

    def get_data(self) -> pd.DataFrame:
        return pd.read_csv(self.data_path, sep=";")


ROIS = [
    RegionOfInterest("MC", "Motor cortex", "#414487"),
    RegionOfInterest("dlPFC", "Dorsolateral prefrontal cortex", "#2a788e"),
    RegionOfInterest("vmPFC", "Ventromedial prefrontal cortex", "#22a884"),
    RegionOfInterest("IPS", "Intraparietal sulcus", "#7ad151"),
]
