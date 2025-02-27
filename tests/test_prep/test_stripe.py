import time
import cupy as cp
from cupy.cuda import nvtx
import numpy as np
import pytest

from httomolibgpu.prep.normalize import normalize
from httomolibgpu.prep.stripe import (
    remove_stripe_based_sorting,
    remove_stripe_ti,
    remove_all_stripe,
    raven_filter,
)
from numpy.testing import assert_allclose
from .stripe_cpu_reference import raven_filter_numpy

def test_remove_stripe_ti_on_data(data, flats, darks):
    # --- testing the CuPy implementation from TomoCupy ---#
    data = normalize(data, flats, darks, cutoff=10, minus_log=True)

    data_after_stripe_removal = remove_stripe_ti(cp.copy(data)).get()

    assert_allclose(np.mean(data_after_stripe_removal), 0.28924704, rtol=1e-05)
    assert_allclose(
        np.mean(data_after_stripe_removal, axis=(1, 2)).sum(), 52.064457, rtol=1e-06
    )
    assert_allclose(np.median(data_after_stripe_removal), 0.026177486, rtol=1e-05)
    assert_allclose(np.max(data_after_stripe_removal), 2.715983, rtol=1e-05)
    assert data_after_stripe_removal.flags.c_contiguous

    data = None  #: free up GPU memory
    # make sure the output is float32
    assert data_after_stripe_removal.dtype == np.float32


# def test_remove_stripe_ti_on_flats(host_flats):
#     #: testing that numpy uint16 arrays can be passed
#     corrected_data = remove_stripe_ti(np.copy(host_flats))
#     assert_allclose(np.mean(corrected_data), 976.558447, rtol=1e-7)
#     assert_allclose(np.mean(corrected_data, axis=(1, 2)).sum(), 19531.168945, rtol=1e-7)
#     assert_allclose(np.median(corrected_data), 976.0, rtol=1e-7)


# def test_remove_stripe_ti_numpy_vs_cupy_on_random_data():
#     host_data = np.random.random_sample(size=(181, 5, 256)).astype(np.float32) * 2.0
#     corrected_host_data = remove_stripe_ti(np.copy(host_data))
#     corrected_data = remove_stripe_ti(
#         cp.copy(cp.asarray(host_data, dtype=cp.float32))
#     ).get()

#     assert_allclose(np.sum(corrected_data), np.sum(corrected_host_data), rtol=1e-6)
#     assert_allclose(
#         np.median(corrected_data), np.median(corrected_host_data), rtol=1e-6
#     )

def test_stripe_removal_sorting_cupy(data, flats, darks):
    # --- testing the CuPy port of TomoPy's implementation ---#
    data = normalize(data, flats, darks, cutoff=10, minus_log=True)
    corrected_data = remove_stripe_based_sorting(data).get()

    data = None  #: free up GPU memory
    assert_allclose(np.mean(corrected_data), 0.288198, rtol=1e-06)
    assert_allclose(np.mean(corrected_data, axis=(1, 2)).sum(), 51.87565, rtol=1e-06)
    assert_allclose(np.sum(corrected_data), 1062413.6, rtol=1e-06)

    # make sure the output is float32
    assert corrected_data.dtype == np.float32
    assert corrected_data.flags.c_contiguous

def test_stripe_raven_cupy(data, flats, darks):
    # --- testing the CuPy port of TomoPy's implementation ---#

    data = normalize(data, flats, darks, cutoff=10, minus_log=True)

    data_after_raven_gpu = raven_filter(cp.copy(data)).get()
    data_after_raven_cpu = raven_filter_numpy(cp.copy(data).get())

    assert_allclose(data_after_raven_cpu, data_after_raven_gpu, rtol=0, atol=4e-01)

    data = None  #: free up GPU memory
    # make sure the output is float32
    assert data_after_raven_gpu.dtype == np.float32
    assert data_after_raven_gpu.shape == data_after_raven_cpu.shape

@pytest.mark.parametrize("uvalue", [20, 50, 100])
@pytest.mark.parametrize("nvalue", [2, 4, 6])
@pytest.mark.parametrize("vvalue", [2, 4])
@pytest.mark.parametrize("pad_x", [0, 10, 20])
@pytest.mark.parametrize("pad_y", [0, 10, 20])
@cp.testing.numpy_cupy_allclose(rtol=0, atol=3e-01)
def test_stripe_raven_parameters_cupy(ensure_clean_memory, xp, uvalue, nvalue, vvalue, pad_x, pad_y):
    # because it's random, we explicitly seed and use numpy only, to match the data
    np.random.seed(12345)
    data = np.random.random_sample(size=(256, 5, 512)).astype(np.float32) * 2.0 + 0.001
    data = xp.asarray(data)

    if xp.__name__ == "numpy":
        results = raven_filter_numpy(
            data, uvalue=uvalue, nvalue=nvalue, vvalue=vvalue, pad_x=pad_x, pad_y=pad_y
        ).astype(np.float32) 
    else:
        results = raven_filter(
            data, uvalue=uvalue, nvalue=nvalue, vvalue=vvalue, pad_x=pad_x, pad_y=pad_y
        ).get()

    return xp.asarray(results)

@pytest.mark.perf
def test_stripe_removal_sorting_cupy_performance(ensure_clean_memory):
    data_host = (
        np.random.random_sample(size=(1801, 5, 2560)).astype(np.float32) * 2.0 + 0.001
    )
    data = cp.asarray(data_host, dtype=np.float32)

    # do a cold run first
    remove_stripe_based_sorting(cp.copy(data))

    dev = cp.cuda.Device()
    dev.synchronize()

    start = time.perf_counter_ns()
    nvtx.RangePush("Core")
    for _ in range(10):
        # have to take copy, as data is modified in-place
        remove_stripe_based_sorting(cp.copy(data))
    nvtx.RangePop()
    dev.synchronize()
    duration_ms = float(time.perf_counter_ns() - start) * 1e-6 / 10

    assert "performance in ms" == duration_ms


@pytest.mark.perf
def test_remove_stripe_ti_performance(ensure_clean_memory):
    data_host = (
        np.random.random_sample(size=(1801, 5, 2560)).astype(np.float32) * 2.0 + 0.001
    )
    data = cp.asarray(data_host, dtype=np.float32)

    # do a cold run first
    remove_stripe_ti(cp.copy(data))

    dev = cp.cuda.Device()
    dev.synchronize()

    start = time.perf_counter_ns()
    nvtx.RangePush("Core")
    for _ in range(10):
        # have to take copy, as data is modified in-place
        remove_stripe_ti(cp.copy(data))
    nvtx.RangePop()
    dev.synchronize()
    duration_ms = float(time.perf_counter_ns() - start) * 1e-6 / 10

    assert "performance in ms" == duration_ms

@pytest.mark.perf
def test_raven_filter_performance(ensure_clean_memory):
    data_host = (
        np.random.random_sample(size=(1801, 5, 2560)).astype(np.float32) * 2.0 + 0.001
    )
    data = cp.asarray(data_host, dtype=np.float32)

    # do a cold run first
    raven_filter(cp.copy(data))

    dev = cp.cuda.Device()
    dev.synchronize()

    start = time.perf_counter_ns()
    nvtx.RangePush("Core")
    for _ in range(10):
        # have to take copy, as data is modified in-place
        raven_filter(cp.copy(data))
    nvtx.RangePop()
    dev.synchronize()
    duration_ms = float(time.perf_counter_ns() - start) * 1e-6 / 10

    assert "performance in ms" == duration_ms

def test_remove_all_stripe_on_data(data, flats, darks):
    # --- testing the CuPy implementation from TomoCupy ---#
    data = normalize(data, flats, darks, cutoff=10, minus_log=True)

    data_after_stripe_removal = remove_all_stripe(cp.copy(data)).get()

    assert_allclose(np.mean(data_after_stripe_removal), 0.266914, rtol=1e-05)
    assert_allclose(
        np.mean(data_after_stripe_removal, axis=(1, 2)).sum(), 48.04459, rtol=1e-06
    )
    assert_allclose(np.median(data_after_stripe_removal), 0.015338, rtol=1e-04)
    assert_allclose(np.max(data_after_stripe_removal), 2.298123, rtol=1e-05)
    assert_allclose(np.median(data_after_stripe_removal, axis=(1, 2)).sum(), 2.788046, rtol=1e-6)
    assert_allclose(np.median(data_after_stripe_removal, axis=(0, 1)).sum(), 28.661312, rtol=1e-6)

    data = None  #: free up GPU memory
    # make sure the output is float32
    assert data_after_stripe_removal.dtype == np.float32
    assert data_after_stripe_removal.flags.c_contiguous


@pytest.mark.perf
def test_remove_all_stripe_performance(ensure_clean_memory):
    data_host = (
        np.random.random_sample(size=(1801, 100, 2560)).astype(np.float32) * 2.0 + 0.001
    )
    data = cp.asarray(data_host, dtype=np.float32)
    remove_all_stripe(cp.copy(data))
    dev = cp.cuda.Device()
    dev.synchronize()
    start = time.perf_counter_ns()
    nvtx.RangePush("Core")
    for _ in range(10):
        # have to take copy, as data is modified in-place
        remove_all_stripe(cp.copy(data))
    nvtx.RangePop()
    dev.synchronize()
    duration_ms = float(time.perf_counter_ns() - start) * 1e-6 / 10

    assert "performance in ms" == duration_ms
