# local
import ivy
from typing import Optional, Union
from ivy.func_wrapper import (
    handle_nestable,
    handle_array_like_without_promotion,
    inputs_to_ivy_arrays,
)
from ivy.utils.exceptions import handle_exceptions
from ivy.functional.ivy.losses import _reduce_loss


@handle_exceptions
@handle_nestable
@handle_array_like_without_promotion
@inputs_to_ivy_arrays
def binary_cross_entropy_with_logits(
    true: Union[ivy.Array, ivy.NativeArray],
    pred: Union[ivy.Array, ivy.NativeArray],
    /,
    *,
    epsilon: float = 1e-7,
    pos_weight: Optional[Union[ivy.Array, ivy.NativeArray]] = None,
    reduction: str = "none",
    out: Optional[ivy.Array] = None,
) -> ivy.Array:
    """
    Compute the binary cross entropy with logits loss.

    Parameters
    ----------
    true
        input array containing true labels.
    pred
        input array containing predicted labels as logits.
    epsilon
        a float in [0.0, 1.0] specifying the amount of smoothing when calculating the
        loss. If epsilon is ``0``, no smoothing will be applied. Default: ``1e-7``.
    pos_weight
        a weight for positive examples. Must be an array with length equal to the number
        of classes.
    out
        optional output array, for writing the result to. It must have a shape
        that the inputs broadcast to.

    Returns
    -------
    ret
        The binary cross entropy with logits loss between the given distributions.


    Examples
    --------
    With :class:`ivy.Array` input:

    >>> x = ivy.array([0, 1, 0, 1])
    >>> y = ivy.array([1.2, 3.8, 5.3, 2.8])
    >>> z = ivy.binary_cross_entropy_with_logits(x, y)
    >>> print(z)
    ivy.array([1.463, 0.022, 5.305, 0.059])

    >>> x = ivy.array([[0, 1, 0, 0]])
    >>> y = ivy.array([[6.6, 4.2, 1.7, 7.3]])
    >>> z = ivy.binary_cross_entropy_with_logits(x, y, epsilon=1e-3)
    >>> print(z)
    ivy.array([[6.601, 0.015, 1.868, 6.908]])

    >>> x = ivy.array([[0, 1, 1, 0]])
    >>> y = ivy.array([[2.6, 6.2, 3.7, 5.3]])
    >>> pos_weight = ivy.array([1.2])
    >>> z = ivy.binary_cross_entropy_with_logits(x, y, pos_weight=pos_weight)
    >>> print(z)
    ivy.array([[2.672, 0.002, 0.029, 5.305]])

    With a mix of :class:`ivy.Array` and :class:`ivy.NativeArray` inputs:

    >>> x = ivy.array([0, 0, 0, 1])
    >>> y = ivy.native_array([3.1, 3.2, 1.8, 4.6])
    >>> z = ivy.binary_cross_entropy_with_logits(x, y)
    >>> print(z)
    ivy.array([3.144, 3.24, 1.953, 0.01])

    With :class:`ivy.Container` input:

    >>> x = ivy.Container(a=ivy.array([1, 1, 0]), b=ivy.array([0, 0, 1]))
    >>> y = ivy.Container(a=ivy.array([3.6, 1.2, 5.3]), b=ivy.array([1.8, 2.2, 1.2]))
    >>> z = ivy.binary_cross_entropy_with_logits(x, y)
    >>> print(z)
    {
        a: ivy.array([0.027, 0.263, 5.305]),
        b: ivy.array([1.953, 2.305, 0.263])
    }

    With a mix of :class:`ivy.Array` and :class:`ivy.Container` inputs:

    >>> x = ivy.array([1, 0, 1])
    >>> y = ivy.Container(a=ivy.array([3.7, 3.8, 1.2]))
    >>> z = ivy.binary_cross_entropy_with_logits(x, y)
    >>> print(z)
    {
        a: ivy.array([0.024, 3.822, 0.263])
    }
    """
    ivy.utils.assertions.check_elem_in_list(reduction, ["none", "sum", "mean"])
    pred = ivy.sigmoid(pred)
    if pos_weight is not None:
        pred = ivy.clip(pred, epsilon, 1 - epsilon)
        result = -(true * -ivy.log(pred) * pos_weight + (1 - true) * -ivy.log(1 - pred))
        result = _reduce_loss(reduction, result, None, out)
    else:
        result = ivy.binary_cross_entropy(
            true,
            pred,
            epsilon=epsilon,
            reduction=reduction,
            out=out,
        )

    return result


@inputs_to_ivy_arrays
@handle_array_like_without_promotion
@handle_nestable
@handle_exceptions
def mse_loss(
    true: Union[ivy.Array, ivy.NativeArray],
    pred: Union[ivy.Array, ivy.NativeArray],
    /,
    *,
    reduction: str = "mean",
    out: Optional[ivy.Array] = None,
) -> ivy.Array:
    """
    Compute the mean squared error (MSE) loss.

    Parameters
    ----------
    true : array-like
        input array containing true values.
    pred : array-like
        input array containing predicted values.
    reduction : {'none', 'mean', 'sum'}, optional
        type of reduction to apply to the output. Default is 'mean'.
    out : array-like, optional
        optional output array, for writing the result to. It must have a shape
        that the inputs broadcast to.

    Returns
    -------
    array
        The MSE loss between the true and predicted values.

    Raises
    -------
    ValueError
        If `reduction` is not one of ['none', 'mean', 'sum'].

    Examples
    --------
    >>> true = ivy.array([1, 2, 3, 4])
    >>> pred = ivy.array([0.9, 2.1, 2.8, 4.2])
    >>> ivy.mse_loss(true, pred)
    ivy.array(0.1075)

    >>> true = ivy.array([[1, 2], [3, 4]])
    >>> pred = ivy.array([[0.8, 2.3], [3.2, 4.1]])
    >>> ivy.mse_loss(true, pred, reduction='sum')
    ivy.array(0.17)

    >>> true = ivy.array([1, 2, 3, 4])
    >>> pred = ivy.array([0.9, 2.1, 2.8, 4.2])
    >>> out = ivy.array([0, 0])
    >>> ivy.mse_loss(true, pred, reduction='none', out=out)
    ivy.array([0.01 , 0.01 ])
    """
    ivy.utils.assertions.check_elem_in_list(reduction, ["none", "sum", "mean"])
    result = ivy.mean(ivy.square(true - pred), keepdims=True)
    return _reduce_loss(reduction, result, None, out)


@inputs_to_ivy_arrays
@handle_array_like_without_promotion
@handle_nestable
@handle_exceptions
def mae_loss(
    true: Union[ivy.Array, ivy.NativeArray],
    pred: Union[ivy.Array, ivy.NativeArray],
    /,
    *,
    reduction: str = "mean",
    out: Optional[ivy.Array] = None,
) -> ivy.Array:
    """
    Compute the mean absolute error (MAE) loss.

    Parameters
    ----------
    true : array-like
        input array containing true values.
    pred : array-like
        input array containing predicted values.
    reduction : {'none', 'mean', 'sum'}, optional
        type of reduction to apply to the output. Default is 'mean'.
    out : array-like, optional
        optional output array, for writing the result to. It must have a shape
        that the inputs broadcast to.

    Returns
    -------
    array
        The MAE loss between the true and predicted values.

    Raises
    -------
    ValueError
        If `reduction` is not one of ['none', 'mean', 'sum'].

    Examples
    --------
    >>> true = ivy.array([1, 2, 3, 4])
    >>> pred = ivy.array([0.9, 2.1, 2.8, 4.2])
    >>> ivy.mae_loss(true, pred)
    ivy.array(0.15)

    >>> true = ivy.array([[1, 2], [3, 4]])
    >>> pred = ivy.array([[0.8, 2.3], [3.2, 4.1]])
    >>> ivy.mae_loss(true, pred, reduction='sum')
    ivy.array(0.8)

    >>> true = ivy.array([1, 2, 3, 4])
    >>> pred = ivy.array([0.9, 2.1, 2.8, 4.2])
    >>> out = ivy.array([0, 0])
    >>> ivy.mae_loss(true, pred, reduction='none', out=out)
    ivy.array([0.1, 0.3])
    """
    ivy.utils.assertions.check_elem_in_list(reduction, ["none", "sum", "mean"])
    result = ivy.mean(ivy.abs(true - pred), keepdims=True)
    return _reduce_loss(reduction, result, None, out)
