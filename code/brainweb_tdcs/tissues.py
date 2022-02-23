from dataclasses import dataclass


@dataclass
class Tissue:

    long_name: str
    k_min: float
    k_max: float
    k_mean: float
    k_std: float
    color: str = "#000000"


TISSUES = {
    "WM": Tissue("white matter", 0.0646, 0.81, 0.2167, 0.1703),
    "GM": Tissue("Gray matter", 0.06, 2.47, 0.466, 0.2392),
    "CSF": Tissue("Cerebrospinal fluid", 1.0, 2.51, 1.71, 0.2981),
    "SKL": Tissue("Skull", 0.0182, 1.718, 0.016, 0.019),
    "SFT": Tissue("Soft tissue", 0.137, 2.1, 0.4137, 0.176),
}
