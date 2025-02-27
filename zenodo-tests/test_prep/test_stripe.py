import cupy as cp
import numpy as np
import pytest

from numpy.testing import assert_allclose
from httomolibgpu.prep.stripe import remove_all_stripe
from httomolibgpu.prep.normalize import normalize
from conftest import force_clean_gpu_memory


@pytest.mark.parametrize(
    "dataset_fixture, exp_sum, mean, mean_sum, med_sum, _med_sum, shape",
    [
        ("i13_dataset1", 32071604.0, 0.208765, 1252.7957, 529.2594, 1254.792, (6001, 10, 2560)),
        ("i13_dataset3", 27234604.0, 0.59093, 3546.1704, 1500.7285, 3531.5493, (6001, 3, 2560)),
    ],
    ids=["dataset_one", "dataset_three"],
)
def test_remove_all_stripe_with_i13_data(
    request, dataset_fixture, exp_sum, mean, mean_sum, med_sum, _med_sum, shape
):
    dataset = request.getfixturevalue(dataset_fixture)
    data_normalised = normalize(dataset[0], dataset[2], dataset[3], minus_log=True)
    output = remove_all_stripe(cp.copy(data_normalised)).get()

    assert_allclose(np.sum(output), exp_sum, rtol=1e-07, atol=1e-6)
    assert_allclose(np.mean(output), mean, rtol=1e-07, atol=1e-6)
    assert_allclose(np.mean(output, axis=(1, 2)).sum(), mean_sum, rtol=1e-06)
    assert_allclose(np.median(output, axis=(0, 1)).sum(), med_sum, rtol=1e-06)
    assert_allclose(np.median(output, axis=(1, 2)).sum(), _med_sum, rtol=1e-6)
    force_clean_gpu_memory()
    assert output.shape == shape
    assert output.dtype == np.float32
    assert output.flags.c_contiguous
