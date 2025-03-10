import os
import cupy as cp
import numpy as np
import pytest
import gc


def pytest_addoption(parser):
    parser.addoption(
        "--performance",
        action="store_true",
        default=False,
        help="run performance tests only",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "perf: mark test as performance test")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--performance"):
        skip_other = pytest.mark.skip(reason="not a performance test")
        for item in items:
            if "perf" not in item.keywords:
                item.add_marker(skip_other)
    else:
        skip_perf = pytest.mark.skip(
            reason="performance test - use '--performance' to run"
        )
        for item in items:
            if "perf" in item.keywords:
                item.add_marker(skip_perf)


CUR_DIR = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope="session")
def test_data_path():
    return os.path.join(CUR_DIR, "large_data_archive")


@pytest.fixture(scope="session")
def i12_dataset1_file(test_data_path):
    in_file = os.path.join(test_data_path, "i12_dataset1.npz")
    return np.load(in_file)


@pytest.fixture
def i12_dataset1(i12_dataset1_file):
    return (
        cp.asarray(i12_dataset1_file["projdata"]),
        i12_dataset1_file["angles"],
        cp.asarray(i12_dataset1_file["flats"]),
        cp.asarray(i12_dataset1_file["darks"]),
    )


@pytest.fixture(scope="session")
def i12_dataset2_file(test_data_path):
    in_file = os.path.join(test_data_path, "i12_dataset2.npz")
    return np.load(in_file)


@pytest.fixture
def i12_dataset2(i12_dataset2_file):
    return (
        cp.asarray(i12_dataset2_file["projdata"]),
        i12_dataset2_file["angles"],
        cp.asarray(i12_dataset2_file["flats"]),
        cp.asarray(i12_dataset2_file["darks"]),
    )


@pytest.fixture(scope="session")
def i12_dataset3_file(test_data_path):
    in_file = os.path.join(test_data_path, "i12_dataset3.npz")
    return np.load(in_file)


@pytest.fixture
def i12_dataset3(i12_dataset3_file):
    return (
        cp.asarray(i12_dataset3_file["proj1"]),
        cp.asarray(i12_dataset3_file["proj2"]),
        cp.asarray(i12_dataset3_file["flats"]),
        cp.asarray(i12_dataset3_file["darks"]),
    )


@pytest.fixture(scope="session")
def i12_dataset4_file(test_data_path):
    in_file = os.path.join(test_data_path, "i12_dataset4.npz")
    return np.load(in_file)


@pytest.fixture
def i12_dataset4(i12_dataset4_file):
    return (
        cp.asarray(i12_dataset4_file["projdata"]),
        i12_dataset4_file["angles"],
        cp.asarray(i12_dataset4_file["flats"]),
        cp.asarray(i12_dataset4_file["darks"]),
    )


@pytest.fixture(scope="session")
def i13_dataset1_file(test_data_path):
    in_file = os.path.join(test_data_path, "i13_dataset1.npz")
    return np.load(in_file)


@pytest.fixture
def i13_dataset1(i13_dataset1_file):
    return (
        cp.asarray(i13_dataset1_file["projdata"]),
        i13_dataset1_file["angles"],
        cp.asarray(i13_dataset1_file["flats"]),
        cp.asarray(i13_dataset1_file["darks"]),
    )


@pytest.fixture(scope="session")
def i13_dataset2_file(test_data_path):
    in_file = os.path.join(test_data_path, "i13_dataset2.npz")
    return np.load(in_file)


@pytest.fixture
def i13_dataset2(i13_dataset2_file):
    return (
        cp.asarray(i13_dataset2_file["projdata"]),
        i13_dataset2_file["angles"],
        cp.asarray(i13_dataset2_file["flats"]),
        cp.asarray(i13_dataset2_file["darks"]),
    )


@pytest.fixture(scope="session")
def i13_dataset3_file(test_data_path):
    in_file = os.path.join(test_data_path, "i13_dataset3.npz")
    return np.load(in_file)


@pytest.fixture
def i13_dataset3(i13_dataset3_file):
    return (
        cp.asarray(i13_dataset3_file["projdata"]),
        i13_dataset3_file["angles"],
        cp.asarray(i13_dataset3_file["flats"]),
        cp.asarray(i13_dataset3_file["darks"]),
    )


@pytest.fixture(scope="session")
def k11_dataset1_file(test_data_path):
    in_file = os.path.join(test_data_path, "k11_dataset1.npz")
    return np.load(in_file)


@pytest.fixture
def k11_dataset1(k11_dataset1_file):
    return (
        cp.asarray(k11_dataset1_file["projdata"]),
        k11_dataset1_file["angles"],
        cp.asarray(k11_dataset1_file["flats"]),
        cp.asarray(k11_dataset1_file["darks"]),
    )


@pytest.fixture(scope="session")
def geant4_dataset1_file(test_data_path):
    in_file = os.path.join(test_data_path, "geant4_dataset1.npz")
    return np.load(in_file)


@pytest.fixture
def geant4_dataset1(geant4_dataset1_file):
    return (
        cp.asarray(geant4_dataset1_file["projdata"]),
        geant4_dataset1_file["angles"],
        cp.asarray(geant4_dataset1_file["flats"]),
        cp.asarray(geant4_dataset1_file["darks"]),
    )


@pytest.fixture(scope="session")
def synth_tomophantom1_file(test_data_path):
    in_file = os.path.join(test_data_path, "synth_tomophantom1.npz")
    return np.load(in_file)


@pytest.fixture
def synth_tomophantom1_dataset(synth_tomophantom1_file):
    return (
        cp.asarray(cp.swapaxes(synth_tomophantom1_file["projdata"], 0, 1)),
        synth_tomophantom1_file["angles"],
    )


@pytest.fixture
def ensure_clean_memory():
    gc.collect()
    cp.get_default_memory_pool().free_all_blocks()
    cp.get_default_pinned_memory_pool().free_all_blocks()
    yield None
    cp.get_default_memory_pool().free_all_blocks()
    cp.get_default_pinned_memory_pool().free_all_blocks()


def force_clean_gpu_memory():
    gc.collect()
    cp.get_default_memory_pool().free_all_blocks()
    cp.get_default_pinned_memory_pool().free_all_blocks()
