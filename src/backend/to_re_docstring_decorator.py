from abc import abstractmethod
from typing import Callable


def to_re_docstring(funcobj: Callable) -> Callable:
    """
    A decorator indicating methods that need to be re-documented by children classes, but is fully functional on its own.

    Based on abc.abstractmethod, so also requires the class to be derived from abc.ABCMeta.
    """
    return abstractmethod(funcobj)