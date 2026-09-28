"""Utility functions for the napari-curviewer package."""

import os


def get_test_path():
    current_script_path = os.path.dirname(os.path.abspath(__file__))
    image_path_1 = os.path.join(
        current_script_path,
        "../../tests/resources/imgtest_01_full_spec_low_res.tif",
    )
    image_path_2 = os.path.join(
        current_script_path,
        "../../tests/resources/imgtest_02_one_root_high_res.tif",
    )
    central_line_2 = os.path.join(
        current_script_path, "../../tests/resources/centralline_02.csv"
    )
    return image_path_1, image_path_2, central_line_2
