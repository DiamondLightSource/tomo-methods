import os
from typing import List, Tuple, Dict

import numpy as np
from scipy.ndimage import map_coordinates


# TODO: Currently is implemented on the CPU, not the GPU
def correct_distortion(data: np.ndarray, metadata_path: str,
                       preview: Dict[str, List[int]],
                       center_from_left: float=None,
                       center_from_top: float=None,
                       polynomial_coeffs: List[float]=None,
                       crop: int=0):
    """Correct the radial distortion in the given stack of 2D images.

    Parameters
    ----------
    data : np.ndarray
        The stack of 2D images to apply the distortion correction to.

    metadata_path : str
        The path to the file containing the distortion coefficients for the
        data.

    preview : Dict[str, List[int]]
        A dict containing three key-value pairs:
        - a list containing the `start` value of each dimension
        - a list containing the `stop` value of each dimension
        - a list containing the `step` value of each dimension

    center_from_left : optional, float
        If no metadata file with the distortion coefficients is provided, then
        the x center can be provided as a parameter by passing the horizontal
        distortion center as measured from the left of the image.

    center_from_top : optional, float
        If no metadata file with the distortion coefficients is provided, then
        the y center can be provided as a parameter by passing the horizontal
        distortion center as measured from the top of the image.

    polynomial_coeffs : optional, List[float]
        If no metadata file with the distortion coefficients is provided, then
        the polynomial coefficients for the distortion correction can be
        provided as a parameter by passing a list of floats.

    crop : optional, int
        The amount to crop both the height and width of the stack of images
        being corrected.

    Returns
    -------
    np.ndarray
        The corrected stack of 2D images.
    """
    # Check if it's a stack of 2D images, or only a single 2D image
    if len(data.shape) == 2:
        data = np.expand_dims(data, axis=0)

    # Get info from metadat txt file
    x_center, y_center, list_fact = _load_metadata_txt(metadata_path)

    shift = preview['starts']
    step = preview['steps']
    x_dim = 1
    y_dim = 0
    step_check = \
        True if max([step[i] for i in [x_dim, y_dim]]) > 1 else False
    if step_check:
        msg = "\n***********************************************\n" \
              "!!! ERROR !!! -> Method doesn't work with the step in" \
              " the preview larger than 1 \n" \
              "***********************************************\n"
        raise ValueError(msg)

    x_offset = shift[x_dim]
    y_offset = shift[y_dim]
    msg = ""
    x_center = 0.0
    y_center = 0.0
    if metadata_path is None:
        x_center = np.asarray(center_from_left, dtype=np.float32) - x_offset
        y_center = np.asarray(center_from_top, dtype=np.float32) - y_offset
        list_fact = np.float32(tuple(polynomial_coeffs))
    else:
        if not (os.path.isfile(metadata_path)):
            msg = "!!! No such file: %s !!!" \
                  " Please check the file path" % str(metadata_path)
            raise ValueError(msg)
        try:
            (x_center, y_center, list_fact) = _load_metadata_txt(
                metadata_path)
            x_center = x_center - x_offset
            y_center = y_center - y_offset
        except IOError:
            msg = "\n*****************************************\n" \
                  "!!! ERROR !!! -> Can't open this file: %s \n" \
                  "*****************************************\n\
                  " % str(metadata_path)
            raise ValueError(msg)

    height, width = data.shape[y_dim+1], data.shape[x_dim+1]
    xu_list = np.arange(width) - x_center
    yu_list = np.arange(height) - y_center
    xu_mat, yu_mat = np.meshgrid(xu_list, yu_list)
    ru_mat = np.sqrt(xu_mat ** 2 + yu_mat ** 2)
    fact_mat = np.sum(
        np.asarray([factor * ru_mat ** i for i,
                                                factor in
                    enumerate(list_fact)]), axis=0)
    xd_mat = np.float32(np.clip(
        x_center + fact_mat * xu_mat, 0, width - 1))
    yd_mat = np.float32(np.clip(
        y_center + fact_mat * yu_mat, 0, height - 1))

    diff_y = np.max(yd_mat) - np.min(yd_mat)
    if (diff_y < 1):
        msg = "\n*****************************************\n\n" \
              "!!! ERROR !!! -> You need to increase the preview" \
              " size for this plugin to work \n\n" \
              "*****************************************\n"
        raise ValueError(msg)

    indices = np.reshape(yd_mat, (-1, 1)), np.reshape(xd_mat, (-1, 1))

    # Loop over images and unwarp them
    for i in range(data.shape[0]):
        mat_corrected = np.reshape(map_coordinates(
            data[i], indices, order=1, mode='reflect'),
            (height, width))
        mat_corrected = mat_corrected[crop:height - crop, crop:width - crop]
        data[i] = mat_corrected
    return mat_corrected


def _load_metadata_txt(file_path):
    """
    Load distortion coefficients from a text file.
    Order of the infor in the text file:
    xcenter
    ycenter
    factor_0
    factor_1
    factor_2
    ...
    Parameters
    ----------
    file_path : str
        Path to the file
    Returns
    -------
    tuple of float and list of floats
        Tuple of (xcenter, ycenter, list_fact).
    """
    with open(file_path, 'r') as f:
        x = f.read().splitlines()
        list_data = []
        for i in x:
            list_data.append(float(i.split()[-1]))
    xcenter = list_data[0]
    ycenter = list_data[1]
    list_fact = list_data[2:]
    return xcenter, ycenter, list_fact
