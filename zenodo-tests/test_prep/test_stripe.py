import cupy as cp
import numpy as np
import pytest

from numpy.testing import assert_allclose
from httomolibgpu.prep.stripe import (
    remove_stripe_based_sorting,
    remove_stripe_ti,
    remove_all_stripe,
    raven_filter,
)
from httomolibgpu.prep.normalize import normalize
from conftest import force_clean_gpu_memory
from math import isclose


@pytest.mark.parametrize(
    "dataset_fixture, size_filt, norm_res_expected",
    [
        (
            "i12_dataset4",
            11,
            78.8627,
        ),
        (
            "i12_dataset4",
            21,
            92.8653,
        ),
        (
            "i12_dataset4",
            31,
            99.6979,
        ),
    ],
    ids=["size_11", "size_21", "size_31"],
)
def test_remove_stripe_based_sorting_i12_dataset4(
    request, dataset_fixture, size_filt, norm_res_expected
):
    dataset = request.getfixturevalue(dataset_fixture)
    data_normalised = normalize(dataset[0], dataset[2], dataset[3], minus_log=True)

    del dataset
    force_clean_gpu_memory()

    output = remove_stripe_based_sorting(
        cp.copy(data_normalised), size=size_filt, dim=1
    )

    residual_calc = data_normalised - output
    norm_res = cp.linalg.norm(residual_calc.flatten())

    assert isclose(norm_res, norm_res_expected, abs_tol=10**-4)

    assert output.dtype == np.float32
    assert output.flags.c_contiguous


@pytest.mark.parametrize(
    "dataset_fixture, beta_val, norm_res_expected",
    [
        (
            "i12_dataset4",
            0.01,
            322.5501,
        ),
        (
            "i12_dataset4",
            0.03,
            173.1643,
        ),
        (
            "i12_dataset4",
            0.06,
            128.8032,
        ),
    ],
    ids=["beta_001", "beta_003", "beta_006"],
)
def test_remove_stripe_ti_i12_dataset4(
    request, dataset_fixture, beta_val, norm_res_expected
):
    dataset = request.getfixturevalue(dataset_fixture)
    data_normalised = normalize(dataset[0], dataset[2], dataset[3], minus_log=True)

    del dataset
    force_clean_gpu_memory()

    output = remove_stripe_ti(cp.copy(data_normalised), beta=beta_val)

    residual_calc = data_normalised - output
    norm_res = cp.linalg.norm(residual_calc.flatten())

    assert isclose(norm_res, norm_res_expected, abs_tol=10**-4)

    assert output.dtype == np.float32
    assert output.flags.c_contiguous


@pytest.mark.parametrize(
    "dataset_fixture, snr_val, la_size_val, sm_size_val, norm_res_expected",
    [
        ("i12_dataset4", 1.0, 31, 10, 105.3542),
        ("i12_dataset4", 2.0, 41, 17, 99.9182),
        ("i12_dataset4", 3.0, 61, 21, 103.3776),
        ("i12_dataset4", 4.0, 71, 31, 106.6767),
    ],
    ids=["snr_1", "snr_2", "snr_3", "snr_4"],
)
def test_remove_all_stripe_i12_dataset4(
    request, dataset_fixture, snr_val, la_size_val, sm_size_val, norm_res_expected
):
    dataset = request.getfixturevalue(dataset_fixture)
    data_normalised = normalize(dataset[0], dataset[2], dataset[3], minus_log=True)

    del dataset
    force_clean_gpu_memory()

    output = remove_all_stripe(
        cp.copy(data_normalised),
        snr=snr_val,
        la_size=la_size_val,
        sm_size=sm_size_val,
        dim=1,
    )

    residual_calc = data_normalised - output
    norm_res = cp.linalg.norm(residual_calc.flatten())

    assert isclose(norm_res, norm_res_expected, abs_tol=10**-4)
    assert not np.isnan(output).any(), "Output contains NaN values"
    assert output.dtype == np.float32
    assert output.flags.c_contiguous


@pytest.mark.parametrize(
    "dataset_fixture, snr_val, la_size_val, sm_size_val, norm_res_expected",
    [
        ("synth_tomophantom1_dataset", 1.0, 61, 21, 53435.61),
        ("synth_tomophantom1_dataset", 0.1, 61, 21, 67917.71),
        ("synth_tomophantom1_dataset", 0.001, 61, 21, 70015.51),
    ],
    ids=["snr_1", "snr_2", "snr_3"],
)
def test_remove_all_stripe_synth_tomophantom1_dataset(
    request, dataset_fixture, snr_val, la_size_val, sm_size_val, norm_res_expected
):
    dataset = request.getfixturevalue(dataset_fixture)
    force_clean_gpu_memory()

    output = remove_all_stripe(
        cp.copy(dataset[0]),
        snr=snr_val,
        la_size=la_size_val,
        sm_size=sm_size_val,
        dim=1,
    )

    residual_calc = dataset[0] - output
    norm_res = cp.linalg.norm(residual_calc.flatten())

    assert isclose(norm_res, norm_res_expected, abs_tol=10**-2)
    assert not np.isnan(output).any(), "Output contains NaN values"
    assert output.dtype == np.float32
    assert output.flags.c_contiguous


@pytest.mark.parametrize(
    "dataset_fixture, nvalue_val, vvalue_val, norm_res_expected",
    [
        ("i12_dataset4", 2, 4, 94.0996),
        ("i12_dataset4", 4, 2, 86.3459),
        ("i12_dataset4", 6, 5, 111.1377),
    ],
    ids=["case_1", "case_2", "case_3"],
)
def test_raven_filter_i12_dataset4(
    request, dataset_fixture, nvalue_val, vvalue_val, norm_res_expected
):
    dataset = request.getfixturevalue(dataset_fixture)
    data_normalised = normalize(
        dataset[0][:, 10:20, :],
        dataset[2][:, 10:20, :],
        dataset[3][:, 10:20, :],
        minus_log=True,
    )

    del dataset
    force_clean_gpu_memory()

    output = raven_filter(
        cp.copy(data_normalised),
        pad_y=20,
        pad_x=20,
        pad_method="edge",
        uvalue=20,
        nvalue=nvalue_val,
        vvalue=vvalue_val,
    )

    residual_calc = data_normalised - output
    norm_res = cp.linalg.norm(residual_calc.flatten())

    assert isclose(norm_res, norm_res_expected, abs_tol=10**-4)

    assert output.dtype == np.float32
    assert output.flags.c_contiguous
