"""
Copyright (c) 2025 Wojciech Kwiatkowski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from abc import abstractmethod
from typing import Callable


def to_re_docstring(func_obj: Callable) -> Callable:
    """
    A decorator indicating methods that need to be re-documented by children classes, but is fully functional on its own.

    Based on abc.abstractmethod, so also requires the class to be derived from abc.ABCMeta.
    """
    return abstractmethod(func_obj)
