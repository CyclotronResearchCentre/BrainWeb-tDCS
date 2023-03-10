from dataclasses import dataclass

import chaospy as cp
from scipy.stats import truncnorm


@dataclass
class Tissue:

    long_name: str
    k_min: float
    k_max: float
    k_mean: float
    k_std: float
    color: str = "#000000"

    @property
    def k(self) -> cp.Distribution:
        return cp.TruncNormal(self.k_min, self.k_max, self.k_mean, self.k_std)

    @property
    def k_norm(self) -> cp.Distribution:
        return cp.Normal(self.k_mean, self.k_std)
    
    @property
    def k_uni(self) -> cp.Distribution:
        return cp.Uniform(self.k_min, self.k_max)


TISSUES = {
    "WM": Tissue("white matter", 0.0646, 0.81, 0.2167, 0.1703, "#440154"),
    "GM": Tissue("Gray matter", 0.06, 2.47, 0.466, 0.2392, "#3a528b"),
    "CSF": Tissue("Cerebrospinal fluid", 1.0, 2.51, 1.71, 0.2981, "#20908c"),
    "SKL": Tissue("Skull", 0.0182, 1.718, 0.016, 0.019, "#5ec961"),
    "SFT": Tissue("Soft tissue", 0.137, 2.1, 0.4137, 0.176, "#fde724"),
}
