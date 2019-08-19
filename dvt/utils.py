# -*- coding: utf-8 -*-
"""Utility functions used across the toolkit.

Public methods may be useful in producing new annotators, aggregators, and
pipeline methods.
"""

from glob import glob
from json import loads, dump
from os.path import(
    abspath,
    dirname,
    expanduser,
    isdir,
    isfile,
    basename,
    join,
    splitext
)
from os import makedirs

from pandas import DataFrame
from numpy import ndarray, array, isin, flatnonzero, uint8, vstack
from cv2 import resize


def process_output_values(values):
    """Take input and create pandas data frame.

    This function standardizes the output from annotators and aggregators in
    order to create the output stored in a DataExtraction object.

    Args:
        values: Either a DataFrame object, None, or dictionary object. If a
            dictionary object, the key should contain lists or ndarrays that
            have the same (leading) dimension. It is also possible to pass a
            dictionary of all scalar values.

    Returns:
        A list of length one, containing a single DataFrame object or a value
        of None (returned if and only if the input is None).
    """
    if isinstance(values, DataFrame):
        return [values]

    if isinstance(values, list) or values is None:
        return values

    assert isinstance(values, dict)

    # convert numpy array into a list of arrays for pandas
    for key in values.keys():
        if isinstance(values[key], ndarray) and len(values[key].shape) > 1:
            values[key] = [x for x in values[key]]

    try:
        dframe = DataFrame(values)
    except ValueError as _:
        dframe = DataFrame(values, index=[0])

    return [dframe]


def sub_image(img, top, right, bottom, left, fct=1, output_shape=None):
    """Take a subset of an input image and return a (resized) subimage.

    Args:
        img (numpy array): Image stored as a three-dimensional image.
        top (int): Top coordinate of the new image.
        right (int): Right coordinate of the new image.
        bottom (int): Bottom coordinate of the new image.
        left (int): Left coordinate of the new image.
        fct (float): Percentage to expand the bounding box by. Defaults to
            1, using the input coordinates as given.
        output_shape (tuple): Size to scale the output image, in pixels. Set
            to None (default) to keep the native resolution.

    Returns:
        A three-dimensional numpy array describing the new image.
    """

    # convert to center, height and width:
    center = [int((top + bottom) / 2), int((left + right) / 2)]
    height = int((bottom - top) / 2 * fct)
    width = int((right - left) / 2 * fct)
    box = [
        center[0] - height,
        center[0] + height,
        center[1] - width,
        center[1] + width,
    ]

    # crop the image as an array
    box[0] = max(0, box[0])
    box[2] = max(0, box[2])
    box[1] = min(img.shape[0], box[1])
    box[3] = min(img.shape[1], box[3])
    crop_img = img[box[0]:box[1], box[2]:box[3], :]

    if output_shape:
        img_scaled = resize(crop_img, output_shape)
    else:
        img_scaled = crop_img

    return uint8(img_scaled)


def setup_tensorflow():
    """Setup options for TensorFlow.

    These options should allow most users to run TensorFlow with either a
    GPU or CPU. It sets several options to avoid keras taking up too much
    memory space and ignore a common warnings about library conflicts that
    can occur on macOS. It also silences verbose warnings from TensorFlow
    that most users can safely ignore.
    """
    from keras.backend.tensorflow_backend import set_session
    from tensorflow import logging, ConfigProto, Session
    from os import environ

    # supress warnings
    logging.set_verbosity(logging.ERROR)
    environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

    # ensure that keras does not use all of the available memory
    config = ConfigProto()
    config.gpu_options.per_process_gpu_memory_fraction = 0.3
    config.gpu_options.visible_device_list = "0"
    set_session(Session(config=config))

    # fix a common local bug
    environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


def pd_col_asarray(pdf, column):
    """Takes a pandas dataframe and column name returns a numpy array.

    Pandas DataFrame columns cannot store numpy array with more than
    one dimension. This is a problem for objects such as image embeddings. We
    instead store these multidimensional arrays a an array of objects. This
    function reconstructs the original array.

    Args:
        pdf (DatFrame): the pandas DataFrame from which to extract the column.
        column (str): Name of the column to extract as a numpy array.
    """
    return vstack(pdf[column].to_list())


def get_data_location():
    """Return location of the data files inclued with the package.
    """
    return join(dirname(__file__), 'data')


def _data_to_json(dframe, path=None, exclude_set=None, exclude_key=None):

    if exclude_set is None:
        exclude_set = set()

    if exclude_key is None:
        exclude_key = set()


    output = {}
    for key, value in dframe.items():
        if value.shape[0] != 0 and key not in exclude_set:
            drop_these = set(exclude_key).intersection(set(value.columns))
            output[key] = loads(value.drop(drop_these).to_json(
                orient='records'
            ))

    if not path:
        return output

    with open(path, "w+") as fin:
        dump(output, fin)

    return None


def _proc_frame_list(frames):
    if frames is not None:
        frames = array(frames)
    return frames


def _which_frames(batch, freq, frames):
    """Determine which frame numbers should be used.
    """
    if frames is None:
        return list(range(0, batch.bsize, freq))

    return flatnonzero(isin(batch.fnames, frames)).tolist()


def _check_out_dir(output_dir, should_exist=False):
    if output_dir is not None:
        output_dir = abspath(expanduser(output_dir))
        if should_exist:
            assert isdir(output_dir)
        elif not isdir(output_dir):
            makedirs(output_dir)

    return output_dir


def _expand_path(path):
    path = abspath(expanduser(path))
    bname = basename(path)
    filename, file_extension = splitext(bname)
    return path, bname, filename, file_extension


def _check_exists(path):
    if not isfile(path):
        raise FileNotFoundError("No such input file found:" + path)

    return path


def _expand_path_and_check(fnames):
    """Expand input paths and make sure
    """
    video_files = []
    for this_name in fnames:
        video_files.extend(glob(this_name, recursive=True))

    video_files = sorted((abspath(x) for x in video_files))
    base_names = [splitext(basename(x))[0] for x in video_files]

    if len(set(base_names)) != len(base_names):
        raise AssertionError(
            "Processing input files with duplicate basenames is not supported."
        )

    if not video_files:
        raise FileNotFoundError("No valid input files found.")

    return video_files


def _trim_bbox(css, image_shape):
    """Given a bounding box and image size, returns a new trimmed bounding box.

    Some algorithms produce bounding boxes that extend over the edges of the
    source image. This function takes such a box and returns a new bounding
    box trimmed to the source.

    Args:
        css (array): An array of dimension four.
        image_shape (array): An array of dimension two.

    Returns:
        An updated bounding box trimmed to the extend of the image.
    """
    return (
        max(css[0], 0),
        min(css[1], image_shape[1]),
        min(css[2], image_shape[0]),
        max(css[3], 0),
    )
