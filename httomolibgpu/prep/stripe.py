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
# Created By  : Tomography Team at DLS <scientificsoftware@diamond.ac.uk>
# Created Date: 01 November 2022
# ---------------------------------------------------------------------------
"""Module for stripes removal"""

import numpy as np
from httomolibgpu import cupywrapper

cp = cupywrapper.cp
cupy_run = cupywrapper.cupy_run

from unittest.mock import Mock

if cupy_run:
    from cupyx.scipy.ndimage import median_filter, binary_dilation, uniform_filter1d
    from cupyx.scipy.fft import fft2, ifft2, fftshift
    from httomolibgpu.cuda_kernels import load_cuda_module
else:
    median_filter = Mock()
    binary_dilation = Mock()
    uniform_filter1d = Mock()
    fft2 = Mock()
    ifft2 = Mock()
    fftshift = Mock()


from typing import Union

__all__ = [
    "remove_stripe_based_sorting",
    "remove_stripe_ti",
    "remove_all_stripe",
    "raven_filter",
]


def remove_stripe_based_sorting(
    data: Union[cp.ndarray, np.ndarray],
    size: int = 11,
    dim: int = 1,
) -> Union[cp.ndarray, np.ndarray]:
    """
    Remove full and partial stripe artifacts from sinogram using Nghia Vo's
    approach, see :cite:`vo2018superior`. This algorithm works particularly
    well for removing partial stripes.

    Steps of the algorithm: 1. Sort each column of the sinogram by its grayscale values.
    2. Apply a smoothing (median) filter on the sorted image along each row. 3. Re-sort the smoothed image columns to the original rows to
    get the corrected sinogram.

    Parameters
    ----------
    data : ndarray
        3D tomographic data as a CuPy or NumPy array.
    size : int, optional
        Window size of the median filter.
    dim : {1, 2}, optional
        Dimension of the window.

    Returns
    -------
    ndarray
        Corrected 3D tomographic data as a CuPy or NumPy array.

    """
    if size is None:
        if data.shape[2] > 2000:
            size = 21
        else:
            size = max(5, int(0.01 * data.shape[2]))

    for m in range(data.shape[1]):
        data[:, m, :] = _rs_sort(data[:, m, :], size, dim)

    return data


def _rs_sort(sinogram, size, dim):
    """
    Remove stripes using the sorting technique.
    """
    sinogram = cp.transpose(sinogram)

    #: Sort each column of the sinogram by its grayscale values
    #: Keep track of the sorting indices so we can reverse it below
    sortvals = cp.argsort(sinogram, axis=1)
    sortvals_reverse = cp.argsort(sortvals, axis=1)
    sino_sort = cp.take_along_axis(sinogram, sortvals, axis=1)

    #: Now apply the median filter on the sorted image along each row
    sino_sort = median_filter(sino_sort, (size, 1) if dim == 1 else (size, size))

    #: step 3: re-sort the smoothed image columns to the original rows
    sino_corrected = cp.take_along_axis(sino_sort, sortvals_reverse, axis=1)

    return cp.transpose(sino_corrected)


def remove_stripe_ti(
    data: Union[cp.ndarray, np.ndarray],
    beta: float = 0.1,
) -> Union[cp.ndarray, np.ndarray]:
    """
    Removes stripes with the method of V. Titarenko (TomoCuPy implementation).
    See :cite:`titarenko2010analytical`.

    Parameters
    ----------
    data : ndarray
        3D stack of projections as a CuPy array.
    beta : float, optional
        filter parameter, lower values increase the filter strength.
        Default is 0.1.

    Returns
    -------
    ndarray
        3D array of de-striped projections.
    """
    # TODO: detector dimensions must be even otherwise error
    gamma = beta * ((1 - beta) / (1 + beta)) ** cp.abs(
        cp.fft.fftfreq(data.shape[-1]) * data.shape[-1]
    )
    gamma[0] -= 1
    v = cp.mean(data, axis=0)
    v = v - v[:, 0:1]
    v = cp.fft.irfft(cp.fft.rfft(v) * cp.fft.rfft(gamma)).astype(data.dtype)
    data[:] += v
    return data


######## Optimized version for Vo-all ring removal in tomopy########
# This function is taken from TomoCuPy package
# *************************************************************************** #
#                  Copyright © 2022, UChicago Argonne, LLC                    #
#                           All Rights Reserved                               #
#                         Software Name: Tomocupy                             #
#                     By: Argonne National Laboratory                         #
#                                                                             #
#                           OPEN SOURCE LICENSE                               #
#                                                                             #
# Redistribution and use in source and binary forms, with or without          #
# modification, are permitted provided that the following conditions are met: #
#                                                                             #
# 1. Redistributions of source code must retain the above copyright notice,   #
#    this list of conditions and the following disclaimer.                    #
# 2. Redistributions in binary form must reproduce the above copyright        #
#    notice, this list of conditions and the following disclaimer in the      #
#    documentation and/or other materials provided with the distribution.     #
# 3. Neither the name of the copyright holder nor the names of its            #
#    contributors may be used to endorse or promote products derived          #
#    from this software without specific prior written permission.            #
#                                                                             #
#                                                                             #
# *************************************************************************** #
def remove_all_stripe(
    data: cp.ndarray,
    snr: float = 3.0,
    la_size: int = 61,
    sm_size: int = 21,
    dim: int = 1,
) -> cp.ndarray:
    """
    Remove all types of stripe artifacts from sinogram using Nghia Vo's
    approach, see :cite:`vo2018superior` (combination of algorithm 3,4,5, and 6).

    Parameters
    ----------
    data : ndarray
        3D tomographic data as a CuPy array.
    snr  : float, optional
        Ratio used to locate large stripes.
        Greater is less sensitive.
    la_size : int, optional
        Window size of the median filter to remove large stripes.
    sm_size : int, optional
        Window size of the median filter to remove small-to-medium stripes.
    dim : {1, 2}, optional
        Dimension of the window.

    Returns
    -------
    ndarray
        Corrected 3D tomographic data as a CuPy or NumPy array.

    """
    matindex = _create_matindex(data.shape[2], data.shape[0])
    for m in range(data.shape[1]):
        sino = data[:, m, :]
        sino = _rs_dead(sino, snr, la_size, matindex)
        sino = _rs_sort(sino, sm_size, dim)
        sino = cp.nan_to_num(sino)
        data[:, m, :] = sino
    return data


def _mpolyfit(x, y):
    n = len(x)
    x_mean = cp.mean(x)
    y_mean = cp.mean(y)

    Sxy = cp.sum(x * y) - n * x_mean * y_mean
    Sxx = cp.sum(x * x) - n * x_mean * x_mean

    slope = Sxy / Sxx
    intercept = y_mean - slope * x_mean
    return slope, intercept


def _detect_stripe(listdata, snr):
    """
    Algorithm 4 in :cite:`Vo:18`. Used to locate stripes.
    """

    numdata = len(listdata)
    listsorted = cp.sort(listdata)[::-1]
    xlist = cp.arange(0, numdata, 1.0)
    ndrop = cp.int16(0.25 * numdata)
    (_slope, _intercept) = _mpolyfit(
        xlist[ndrop : -ndrop - 1], listsorted[ndrop : -ndrop - 1]
    )

    numt1 = _intercept + _slope * xlist[-1]
    noiselevel = cp.abs(numt1 - _intercept)
    noiselevel = cp.clip(noiselevel, 1e-6, None)
    val1 = cp.abs(listsorted[0] - _intercept) / noiselevel
    val2 = cp.abs(listsorted[-1] - numt1) / noiselevel
    listmask = cp.zeros_like(listdata)
    if val1 >= snr:
        upper_thresh = _intercept + noiselevel * snr * 0.5
        listmask[listdata > upper_thresh] = 1.0
    if val2 >= snr:
        lower_thresh = numt1 - noiselevel * snr * 0.5
        listmask[listdata <= lower_thresh] = 1.0
    return listmask


def _rs_large(sinogram, snr, size, matindex, drop_ratio=0.1, norm=True):
    """
    Remove large stripes.
    """
    drop_ratio = max(min(drop_ratio, 0.8), 0)  # = cp.clip(drop_ratio, 0.0, 0.8)
    (nrow, ncol) = sinogram.shape
    ndrop = int(0.5 * drop_ratio * nrow)
    sinosort = cp.sort(sinogram, axis=0)
    sinosmooth = median_filter(sinosort, (1, size))
    list1 = cp.mean(sinosort[ndrop : nrow - ndrop], axis=0)
    list2 = cp.mean(sinosmooth[ndrop : nrow - ndrop], axis=0)
    listfact = list1 / list2

    # Locate stripes
    listmask = _detect_stripe(listfact, snr)
    listmask = binary_dilation(listmask, iterations=1).astype(listmask.dtype)
    matfact = cp.tile(listfact, (nrow, 1))
    # Normalize
    if norm is True:
        sinogram = sinogram / matfact
    sinogram1 = cp.transpose(sinogram)
    matcombine = cp.asarray(cp.dstack((matindex, sinogram1)))

    ids = cp.argsort(matcombine[:, :, 1], axis=1)
    matsort = matcombine.copy()
    matsort[:, :, 0] = cp.take_along_axis(matsort[:, :, 0], ids, axis=1)
    matsort[:, :, 1] = cp.take_along_axis(matsort[:, :, 1], ids, axis=1)

    matsort[:, :, 1] = cp.transpose(sinosmooth)
    ids = cp.argsort(matsort[:, :, 0], axis=1)
    matsortback = matsort.copy()
    matsortback[:, :, 0] = cp.take_along_axis(matsortback[:, :, 0], ids, axis=1)
    matsortback[:, :, 1] = cp.take_along_axis(matsortback[:, :, 1], ids, axis=1)

    sino_corrected = cp.transpose(matsortback[:, :, 1])
    listxmiss = cp.where(listmask > 0.0)[0]
    sinogram[:, listxmiss] = sino_corrected[:, listxmiss]
    return sinogram


def _rs_dead(sinogram, snr, size, matindex, norm=True):
    """remove unresponsive and fluctuating stripes"""
    sinogram = cp.copy(sinogram)  # Make it mutable
    (nrow, _) = sinogram.shape
    sinosmooth = uniform_filter1d(sinogram, 10, axis=0)

    listdiff = cp.sum(cp.abs(sinogram - sinosmooth), axis=0)
    listdiffbck = median_filter(listdiff, size)

    listfact = listdiff / listdiffbck

    listmask = _detect_stripe(listfact, snr)
    del listfact
    listmask = binary_dilation(listmask, iterations=1).astype(listmask.dtype)
    listmask[0:2] = 0.0
    listmask[-2:] = 0.0

    listx = cp.where(listmask < 1.0)[0]
    listxmiss = cp.where(listmask > 0.0)[0]
    del listmask

    if len(listxmiss) > 0:
        ids = cp.searchsorted(listx, listxmiss)
        weights = (listxmiss - listx[ids - 1]) / (listx[ids] - listx[ids - 1])
        # direct interpolation without making an extra copy
        sinogram[:, listxmiss] = (
            sinogram[:, listx[ids - 1]] +
            weights * (sinogram[:, listx[ids]] - sinogram[:, listx[ids - 1]])
        )

    # Remove residual stripes
    if norm is True:
        sinogram = _rs_large(sinogram, snr, size, matindex)
    return sinogram


def raven_filter(
    data: cp.ndarray,
    pad_y: int = 20,
    pad_x: int = 20,
    pad_method: str = "edge",
    uvalue: int = 20,
    nvalue: int = 4,
    vvalue: int = 2,
) -> cp.ndarray:
    """
    Applies FFT-based Raven filter :cite:`raven1998numerical` to a 3D CuPy array. For more detailed information, see :ref:`method_raven_filter`.

    Parameters
    ----------
    data : cp.ndarray
        Input CuPy 3D array either float32 or uint16 data type.

    pad_y : int, optional
        Pad the top and bottom of projections.

    pad_x : int, optional
        Pad the left and right of projections.

    pad_method : str, optional
        Numpy pad method to use.

    uvalue : int, optional
        Cut-off frequency. To control the strength of filter, e.g., strong=10, moderate=20, weak=50.

    nvalue : int, optional
        The shape of filter.

    vvalue : int, optional
        Number of image-rows around the zero-frequency to be applied the filter.

    Returns
    -------
    cp.ndarray
        Raven filtered 3D CuPy array in float32 data type.

    Raises
    ------
    ValueError
        If the input array is not three dimensional.
    """

    if data.dtype != cp.float32:
        raise ValueError("The input data should be float32 data type")

    # Padding of the sinogram
    data = cp.pad(data, ((pad_y, pad_y), (0, 0), (pad_x, pad_x)), mode=pad_method)

    # FFT and shift of sinogram
    fft_data = fft2(data, axes=(0, 2), overwrite_x=True)
    fft_data_shifted = fftshift(fft_data, axes=(0, 2))

    # Calculation type
    calc_type = fft_data_shifted.dtype

    # Setup various values for the filter
    height, images, width = data.shape

    # Set the input type of the kernel
    kernel_args = "raven_filter<{0}>".format(
        "float" if calc_type == "complex64" else "double"
    )

    # setting grid/block parameters
    block_x = 128
    block_dims = (block_x, 1, 1)
    grid_x = (width + block_x - 1) // block_x
    grid_y = images
    grid_z = height
    grid_dims = (grid_x, grid_y, grid_z)
    params = (fft_data_shifted, fft_data, width, images, height, uvalue, nvalue, vvalue)

    raven_module = load_cuda_module("raven_filter", name_expressions=[kernel_args])
    raven_filt = raven_module.get_function(kernel_args)

    raven_filt(grid_dims, block_dims, params)
    del fft_data_shifted

    # raven_filt already doing ifftshifting
    data = ifft2(fft_data, axes=(0, 2), overwrite_x=True)

    # Removing padding
    data = data[pad_y : height - pad_y, :, pad_x : width - pad_x].real

    return data


def _create_matindex(nrow, ncol):
    """
    Create a 2D array of indexes used for the sorting technique.
    """
    listindex = cp.arange(0.0, ncol, 1.0)
    matindex = cp.tile(listindex, (nrow, 1))
    return matindex.astype(np.float32)
