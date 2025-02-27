import cupy as cp
import numpy as np
import pytest
from cupy.cuda import nvtx
import time
from math import isclose

from httomolibgpu.prep.normalize import normalize
from httomolibgpu.recon.algorithm import (
    FBP,
    LPRec,
)
from httomolibgpu.misc.morph import sino_360_to_180
from numpy.testing import assert_allclose
import time
import pytest
from cupy.cuda import nvtx
from conftest import force_clean_gpu_memory


def test_reconstruct_FBP_i12_dataset1(i12_dataset1):
    force_clean_gpu_memory()
    projdata = i12_dataset1[0]
    angles = i12_dataset1[1]
    flats = i12_dataset1[2]
    darks = i12_dataset1[3]
    del i12_dataset1

    data_normalised = normalize(projdata, flats, darks, minus_log=True)
    del flats, darks, projdata
    force_clean_gpu_memory()

    recon_data = FBP(
        data_normalised,
        np.deg2rad(angles),
        center=1253.75,
        filter_freq_cutoff=0.35,
    )
    assert recon_data.flags.c_contiguous
    recon_data = recon_data.get()
    assert_allclose(np.sum(recon_data), 46569.39, rtol=1e-07, atol=1e-6)
    assert recon_data.dtype == np.float32
    assert recon_data.shape == (2560, 50, 2560)


def test_reconstruct_LP_REC_i13_dataset1(i13_dataset1):
    force_clean_gpu_memory()
    projdata = i13_dataset1[0]
    angles = i13_dataset1[1]
    flats = i13_dataset1[2]
    darks = i13_dataset1[3]
    del i13_dataset1

    data_normalised = normalize(projdata, flats, darks, minus_log=True)
    del flats, darks, projdata
    force_clean_gpu_memory()

    stiched_data_180degrees = sino_360_to_180(
        data_normalised[:, 2:3, :], overlap=473.822265625, rotation="right"
    )
    del data_normalised
    force_clean_gpu_memory()

    # GPU archetictures older than 5.3 wont accept the data larger than
    # (4096, 4096, 4096), while the newer ones can accept (16384 x 16384 x 16384)

    # recon_data = FBP(
    #     stiched_data_180degrees,
    #     np.deg2rad(angles[0:3000]),
    #     center=2322,
    #     filter_freq_cutoff=0.35,
    # )
    recon_data = LPRec(
        data=stiched_data_180degrees,
        angles=np.deg2rad(angles[0:3000]),
        center=2322.08,
    )

    assert recon_data.flags.c_contiguous
    recon_data = recon_data.get()
    assert isclose(np.sum(recon_data), 620.856, abs_tol=10**-3)
    assert recon_data.dtype == np.float32
    assert recon_data.shape == (4646, 1, 4646)


@pytest.mark.perf
def test_FBP_performance_i13_dataset2(i13_dataset2):
    force_clean_gpu_memory()
    dev = cp.cuda.Device()
    projdata = i13_dataset2[0]
    angles = i13_dataset2[1]
    flats = i13_dataset2[2]
    darks = i13_dataset2[3]
    del i13_dataset2

    data_normalised = normalize(projdata, flats, darks, minus_log=True)
    del flats, darks, projdata
    force_clean_gpu_memory()

    # cold run first
    FBP(
        data_normalised,
        np.deg2rad(angles),
        center=1253.75,
        filter_freq_cutoff=0.35,
    )
    dev.synchronize()

    start = time.perf_counter_ns()
    nvtx.RangePush("Core")
    for _ in range(10):
        FBP(
            data_normalised,
            np.deg2rad(angles),
            center=1286.25,
            filter_freq_cutoff=0.35,
        )
    nvtx.RangePop()
    dev.synchronize()
    duration_ms = float(time.perf_counter_ns() - start) * 1e-6 / 10

    assert "performance in ms" == duration_ms


def test_reconstruct_LPREC_i13_dataset2(i13_dataset2):
    force_clean_gpu_memory()
    projdata = i13_dataset2[0]
    angles = i13_dataset2[1]
    flats = i13_dataset2[2]
    darks = i13_dataset2[3]
    del i13_dataset2

    data_normalised = normalize(projdata, flats, darks, minus_log=True)
    del flats, darks, projdata
    force_clean_gpu_memory()

    recon_data = LPRec(
        data=data_normalised,
        angles=np.deg2rad(angles),
        center=1286.25,
    )
    assert recon_data.flags.c_contiguous
    recon_data = recon_data.get()

    assert isclose(np.sum(recon_data), 2044.953, abs_tol=10**-3)
    assert recon_data.dtype == np.float32
    assert recon_data.shape == (2560, 10, 2560)


@pytest.mark.perf
def test_LPREC_performance_i13_dataset2(i13_dataset2):
    dev = cp.cuda.Device()
    projdata = i13_dataset2[0]
    angles = i13_dataset2[1]
    flats = i13_dataset2[2]
    darks = i13_dataset2[3]
    del i13_dataset2

    data_normalised = normalize(projdata, flats, darks, minus_log=True)
    del flats, darks, projdata
    force_clean_gpu_memory()

    # cold run first
    LPRec(
        data=data_normalised,
        angles=np.deg2rad(angles),
        center=1286.25,
    )
    dev.synchronize()

    start = time.perf_counter_ns()
    nvtx.RangePush("Core")
    for _ in range(10):
        LPRec(
            data=data_normalised,
            angles=np.deg2rad(angles),
            center=1286.25,
        )
    nvtx.RangePop()
    dev.synchronize()
    duration_ms = float(time.perf_counter_ns() - start) * 1e-6 / 10

    assert "performance in ms" == duration_ms


def test_reconstruct_FBP_i13_dataset3(i13_dataset3):
    force_clean_gpu_memory()
    projdata = i13_dataset3[0]
    angles = i13_dataset3[1]
    flats = i13_dataset3[2]
    darks = i13_dataset3[3]
    del i13_dataset3

    data_normalised = normalize(projdata, flats, darks, minus_log=True)
    del flats, darks, projdata
    force_clean_gpu_memory()

    stiched_data_180degrees = sino_360_to_180(
        data_normalised, overlap=438.173828, rotation="left"
    )
    force_clean_gpu_memory()

    # GPU archetictures older than 5.3 wont accept the data larger than
    # (4096, 4096, 4096), while the newer ones can accept (16384 x 16384 x 16384)

    recon_data = FBP(
        stiched_data_180degrees,
        np.deg2rad(angles[0:3000]),
        center=2341,
        filter_freq_cutoff=0.35,
    )

    assert recon_data.flags.c_contiguous
    recon_data = recon_data.get()
    assert recon_data.dtype == np.float32
    assert recon_data.shape == (4682, 3, 4682)
