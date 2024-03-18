import cv2
import numpy as np


def foo():
    assert False, "foo_foo"


def bar():
    array = np.ndarray([1, 2, 3])
    raise TypeError("foo_bar")


def egg():
    x = object()
    raise FileNotFoundError("foo_egg")


def ham():
    cv2.redirectError(blank)
    vc = cv2.VideoCapture('no/such/file.mp4')
    r, f = vc.read()
    cv2.imwrite('no/such/file.jpeg', f)
    return vc


def blank(*args, **kwargs):
    pass
