# global
import math
from numbers import Number
import numpy as np
from typing import Optional, Union, Tuple, Sequence, Callable, Literal

# local
import ivy


def vorbis_window(
    window_length: np.ndarray,
    *,
    dtype: Optional[np.dtype] = np.float32,
    out: Optional[np.ndarray] = None,
) -> np.ndarray:
    return np.array(
        [
            round(
                math.sin(
                    (ivy.pi / 2) * (math.sin(ivy.pi * (i) / (window_length * 2)) ** 2)
                ),
                8,
            )
            for i in range(1, window_length * 2)[0::2]
        ],
        dtype=dtype,
    )


vorbis_window.support_native_out = False


def hann_window(
    window_length: int,
    periodic: Optional[bool] = True,
    dtype: Optional[np.dtype] = None,
    *,
    out: Optional[np.ndarray] = None,
) -> np.ndarray:
    window_length = window_length + 1 if periodic is True else window_length
    return np.array(np.hanning(window_length), dtype=dtype)


hann_window.support_native_out = False


def max_pool2d(
    x: np.ndarray,
    kernel: Union[int, Tuple[int], Tuple[int, int]],
    strides: Union[int, Tuple[int], Tuple[int, int]],
    padding: str,
    /,
    *,
    data_format: str = "NHWC",
    out: Optional[np.ndarray] = None,
) -> np.ndarray:

    if isinstance(kernel, int):
        kernel = [kernel] * 2
    elif len(kernel) == 1:
        kernel = [kernel[0]] * 2

    if isinstance(strides, int):
        strides = [strides] * 2
    elif len(strides) == 1:
        strides = [strides[0]] * 2

    if data_format == "NCHW":
        x = np.transpose(x, (0, 2, 3, 1))

    x_shape = list(x.shape[1:3])
    pad_h = ivy.handle_padding(x_shape[0], strides[0], kernel[0], padding)
    pad_w = ivy.handle_padding(x_shape[1], strides[1], kernel[1], padding)
    x = np.pad(
        x,
        [
            (0, 0),
            (pad_h // 2, pad_h - pad_h // 2),
            (pad_w // 2, pad_w - pad_w // 2),
            (0, 0),
        ],
        "edge",
    )

    x_shape = x.shape
    new_h = (x_shape[1] - kernel[0]) // strides[0] + 1
    new_w = (x_shape[2] - kernel[1]) // strides[1] + 1
    new_shape = [x_shape[0], new_h, new_w] + list(kernel) + [x_shape[-1]]
    new_strides = (
        x.strides[0],
        x.strides[1] * strides[1],
        x.strides[2] * strides[0],
        x.strides[1],
        x.strides[2],
        x.strides[3],
    )
    # B x OH x OW x KH x KW x I
    sub_matrices = np.lib.stride_tricks.as_strided(
        x, new_shape, new_strides, writeable=False
    )

    # B x OH x OW x O
    res = sub_matrices.max(axis=(3, 4))
    if data_format == "NCHW":
        return np.transpose(res, (0, 3, 1, 2))
    return res


def _flat_array_to_1_dim_array(x):
    return x.reshape((1,)) if x.shape == () else x


def pad(
    x: np.ndarray,
    /,
    pad_width: Union[Sequence[Sequence[int]], np.ndarray, int],
    *,
    mode: Optional[
        Union[
            Literal[
                "constant",
                "edge",
                "linear_ramp",
                "maximum",
                "mean",
                "median",
                "minimum",
                "reflect",
                "symmetric",
                "wrap",
                "empty",
            ],
            Callable,
        ]
    ] = "constant",
    stat_length: Optional[Union[Sequence[Sequence[int]], int]] = None,
    constant_values: Optional[Union[Sequence[Sequence[Number]], Number]] = 0,
    end_values: Optional[Union[Sequence[Sequence[Number]], Number]] = 0,
    reflect_type: Optional[Literal["even", "odd"]] = "even",
    out: Optional[np.ndarray] = None,
) -> np.ndarray:
    if mode in ["maximum", "mean", "median", "minimum"]:
        return np.pad(
            _flat_array_to_1_dim_array(x),
            pad_width,
            mode=mode,
            stat_length=stat_length,
        )
    elif mode == "constant":
        return np.pad(
            _flat_array_to_1_dim_array(x),
            pad_width,
            mode=mode,
            constant_values=constant_values,
        )
    elif mode == "linear_ramp":
        return np.pad(
            _flat_array_to_1_dim_array(x),
            pad_width,
            mode=mode,
            end_values=end_values,
        )
    elif mode in ["reflect", "symmetric"]:
        return np.pad(
            _flat_array_to_1_dim_array(x),
            pad_width,
            mode=mode,
            reflect_type=reflect_type,
        )
    else:
        return np.pad(
            _flat_array_to_1_dim_array(x),
            pad_width,
            mode=mode,
        )


def kaiser_window(
    window_length: int,
    periodic: bool = True,
    beta: float = 12.0,
    *,
    dtype: Optional[np.dtype] = None,
    out: Optional[np.ndarray] = None,
) -> np.ndarray:
    if periodic is False:
        return np.array(np.kaiser(M=window_length, beta=beta), dtype=dtype)
    else:
        return np.array(np.kaiser(M=window_length + 1, beta=beta)[:-1], dtype=dtype)


kaiser_window.support_native_out = False