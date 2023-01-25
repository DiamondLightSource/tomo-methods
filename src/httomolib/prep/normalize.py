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
# version ='0.1'
# ---------------------------------------------------------------------------
"""Modules for raw projection data normalization"""

import cupy as cp
from cupy import float32, log, mean, ndarray

__all__ = [
    'normalize_cupy',
    'normalize_raw_cuda',
]


def normalize_raw_cuda(
    data: ndarray,
    flats: ndarray,
    darks: ndarray,
    gpu_id : int = 0,
    cutoff: float = 10.0,
    minus_log: bool = False,
    nonnegativity: bool = False
) -> ndarray:
    """
    Normalize raw projection data using the flat and dark field projections.
    This is a raw CUDA kernel implementation with CuPy wrappers.

    Parameters
    ----------
    data : cp.ndarray
        Projection data as a CuPy array.
    flats : cp.ndarray
        3D flat field data as a CuPy array.
    darks : cp.ndarray
        3D dark field data as a CuPy array.
    gpu_id : int, optional
        A GPU device index to perform operation on.        
    cutoff : float, optional
        Permitted maximum value for the normalised data.
    minus_log : bool, optional
        Apply negative log to the normalised data.
    nonnegativity : bool, optional
        Remove negative values in the normalised data.          

    Returns
    -------
    cp.ndarray
        Normalised 3D tomographic data as a CuPy array.
    """

    cp.cuda.Device(gpu_id).use()
    
    dark0 = mean(darks, axis=0, dtype=float32)
    flat0 = mean(flats, axis=0, dtype=float32)
    out = cp.zeros(data.shape, dtype=float32)

    norm_kernel = cp.RawKernel(
        """extern "C" __global__ void normalize(const unsigned short* data,
           const float* flat,
           const float* dark,
           float* out, float cutoff, int take_log_param, int nonnegativity_param, int A, int B)
           {
             int bid = blockIdx.x;
             int tx = threadIdx.x;
             int ty = threadIdx.y;
             data += bid * A * B;
             out += bid * A * B;
             long long index;            
             
             for (int a = ty; a < A; a += blockDim.y)
    	     {
 	     #pragma unroll(4)
	            for (int b = tx; b < B; b += blockDim.x)
	            {
                    index = a * B + b;
                    float denom = flat[index] - dark[index];
                    if (denom < 1.0f)
                    {
                    denom = 1.0f;
                    }
                    float tmp = (float(data[index]) - dark[index]) / denom;
                    if (tmp > cutoff)
                    {
                    tmp = cutoff;
                    }      
                    if (take_log_param == 1)
                    {
                        tmp = -logf(tmp);
                    }
                    if (nonnegativity_param == 1)
                    {
                        if (tmp < 0.0f) {tmp = 0.0f;}
                    }
	        out[index] = tmp;
    	        }
	        }
           }""", "normalize")

    grids = (32, 32, 1)
    blocks = (data.shape[0], 1, 1)
    params = (data, flat0, dark0, out, float32(cutoff),
              minus_log, nonnegativity, data.shape[1], data.shape[2])
    norm_kernel(grids, blocks, params)

    return out


#: CuPy implementation with higher memory footprint than normalize_raw_cuda.
def normalize_cupy(
    data: ndarray,
    flats: ndarray,
    darks: ndarray,
    gpu_id : int = 0,
    cutoff: float = 10.0,
    minus_log: bool = False,
    nonnegativity: bool = False,
    remove_nans: bool = False
) -> ndarray:
    """
    Normalize raw projection data using the flat and dark field projections.    

    Parameters
    ----------
    data : ndarray
        3D stack of projections as a CuPy array.
    flats : ndarray
        2D or 3D flat field data as a CuPy array.
    darks : ndarray
        2D or 3D dark field data as a CuPy array.
    gpu_id : int, optional
        A GPU device index to perform operation on.
    cutoff : float, optional
        Permitted maximum value for the normalised data.
    minus_log : bool, optional
        Apply negative log to the normalised data.
    nonnegativity : bool, optional
        Remove negative values in the normalised data.
    remove_nans : bool, optional
        Remove NaN values in the normalised data.
        
    Returns
    -------
    ndarray
        Normalised 3D tomographic data as a CuPy array.
    """
    cp.cuda.Device(gpu_id).use()
    
    darks = mean(darks, axis=0, dtype=float32)
    flats = mean(flats, axis=0, dtype=float32)

    if data.ndim != 3:
        raise ValueError("Input data must be a 3D stack of projections")

    if flats.ndim == 2:
        flats = flats[cp.newaxis, :, :]
    if darks.ndim == 2:
        darks = darks[cp.newaxis, :, :]

    if flats.ndim not in (2, 3):
        raise ValueError("Input flats must be 2D or 3D data only")

    if darks.ndim not in (2, 3):
        raise ValueError("Input darks must be 2D or 3D data only")

    # replicates tomopy implementation
    denom = (flats - darks)
    denom[denom < 1.0] = 1.0
    # implicitly assumes as if flats/darks is integer data type
    data = (data - darks) / denom
    data[data > cutoff] = cutoff

    if minus_log:
        data = -log(data)
    if nonnegativity:
        data[data < 0.0] = 0.0
    if remove_nans:
        data[cp.isnan(data)] = 0

    return data
