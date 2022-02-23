import ipywidgets as widgets

from . import EXPERIMENTS, ROIS


def experiment_selector() -> widgets.Dropdown:
    return widgets.Dropdown(
        options=[(str(e), i) for i, e in enumerate(EXPERIMENTS)],
        value=0,
        description="Experiment:",
    )


def roi_selector() -> widgets.Dropdown:
    return widgets.Dropdown(
        options=[(str(r), i) for i, r in enumerate(ROIS)], value=0, description="ROI:"
    )


def roi_selector_bi_uni() -> widgets.Dropdown:
    return widgets.Dropdown(
        options=[(str(r), i) for i, r in enumerate(ROIS[:2])],
        value=0,
        description="ROI:",
    )
