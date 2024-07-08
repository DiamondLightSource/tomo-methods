#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Copyright 2022 Diamond Light Source Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------------------------------------------------------

import os
import sys
import argparse
from typing import Union
import numpy as np
import cupy
import cupy as cp
from PIL import Image


# usage : python -m methods_to_generate_images -i /home/algol/Documents/DEV/httomolibgpu/tests/test_data/synthdata_nxtomo1.npz -o /home/algol/Documents/DEV/httomolibgpu/docs/source/_static/auto_images_methods


def __save_res_to_image(
    result: np.ndarray,
    output_folder: str,
    methods_name: str,
    slice_numb: int,
    max_scale: Union[float, None] = None,
    min_scale: Union[float, None] = None,
):
    """Saving the result of the method into the image

    Args:
        result (np.ndarray): A numpy array to save
        output_folder (str): Path to output folder
        methods_name (str): the name of the method
        slice_numb (int): Slice number to save
        max_scale (float, None): if a specific rescaling needed
        min_scale (float, None): if a specific rescaling needed

    Returns:
    """
    if min_scale is None and max_scale is None:
        result = (result - result.min()) / (result.max() - result.min())
    else:
        result = (result - min_scale) / (max_scale - min_scale)
    resut_to_save = Image.fromarray((result[:, slice_numb, :] * 255).astype(np.uint8))
    resut_to_save.save(output_folder + methods_name + "_sino.png")

    resut_to_save = Image.fromarray((result[slice_numb, :, :] * 255).astype(np.uint8))
    resut_to_save.save(output_folder + methods_name + "_proj.png")


def run_methods(path_to_data: str, output_folder: str) -> int:
    """function that selectively runs the methods with the test data provided and save the result as an image

    Args:
        path_to_data: A path to the test data.
        output_folder: path to output folder with the saved images.

    Returns:
        returns zero if the processing is successful
    """
    try:
        fileloaded = np.load(path_to_data)
    except OSError:
        print("Cannot find/open file {}".format(path_to_data))
        sys.exit()
    print("Unpacking data file...\n")
    proj_raw = fileloaded["proj_raw"]
    proj_ground_truth = fileloaded["proj_ground_truth"]
    phantom = fileloaded["phantom"]
    flats = fileloaded["flats"]
    darks = fileloaded["darks"]
    angles_degr = fileloaded["angles"]

    slice_numb = 40

    __save_res_to_image(
        proj_raw,
        output_folder,
        methods_name="raw_data",
        slice_numb=slice_numb,
    )

    __save_res_to_image(
        proj_ground_truth,
        output_folder,
        methods_name="proj_ground_truth",
        slice_numb=slice_numb,
    )
    __save_res_to_image(darks, output_folder, methods_name="darks", slice_numb=10)
    __save_res_to_image(flats, output_folder, methods_name="flats", slice_numb=10)

    #
    # proj_ground_truth = cp.asarray(proj_ground_truth)
    # phantom = cp.asarray(phantom)
    # flats = cp.asarray(flats)
    # darks = cp.asarray(darks)

    print("Executing methods from the HTTomolibGPU library\n")

    methods_name = "normalisation"
    print("___{}___".format(methods_name))
    from httomolibgpu.prep.normalize import normalize

    data_normalized = normalize(
        cp.asarray(proj_raw), cp.asarray(flats), cp.asarray(darks), minus_log=True
    )

    __save_res_to_image(data_normalized.get(), output_folder, methods_name, slice_numb)

    methods_name = "median_filter"
    print("___{}___".format(methods_name))
    from httomolibgpu.misc.corr import (
        median_filter,
        remove_outlier,
    )

    proj_raw_mod = np.copy(proj_raw)
    proj_raw_mod[slice_numb, 20:22, 20:22] = 0.0
    proj_raw_mod[slice_numb, 60:65, 70:71] = 0.0
    proj_raw_mod[200:210, slice_numb, 200] = 0.0

    __save_res_to_image(
        proj_raw_mod,
        output_folder,
        methods_name=methods_name + "_input",
        slice_numb=slice_numb,
    )

    outlier_removal_cp = remove_outlier(
        cp.asarray(proj_raw_mod, dtype=cp.float32),
        kernel_size=5,
        axis=None,
        dif=2000,
    )
    outlier_removal_np = outlier_removal_cp.get()

    __save_res_to_image(
        outlier_removal_np,
        output_folder,
        methods_name,
        slice_numb,
        max_scale=np.max(proj_raw_mod),
        min_scale=np.min(proj_raw_mod),
    )
    __save_res_to_image(
        np.abs(proj_raw_mod - outlier_removal_np),
        output_folder,
        methods_name=methods_name + "_res",
        slice_numb=slice_numb,
    )
    del outlier_removal_cp

    return 0


def get_args():
    parser = argparse.ArgumentParser(
        description="Script that executes methods and "
        "generates images to be added to documentation."
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default=None,
        help="A path to the test data.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="./",
        help="Directory to save the images.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    current_dir = os.path.basename(os.path.abspath(os.curdir))
    args = get_args()
    path_to_data = args.input
    output_folder = args.output
    return_val = run_methods(path_to_data, output_folder)
    if return_val == 0:
        print("The images have been successfully generated!")
