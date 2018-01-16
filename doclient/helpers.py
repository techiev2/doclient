#! coding=utf-8
"""DigitalOcean APIv2 helpers module"""
__author__ = "Sriram Velamur <sriram.velamur@gmail.com>"
__all__ = ("set_caller",)

import sys
sys.dont_write_bytecode = True


def set_caller(function):
    r"""
    Decorator to set reference DOClient object to callee object instance.
    """
    def wrapper(cls, *args, **kwargs):
        """Wrapper method"""
        frame_locals = getattr(sys, "_getframe")(1).f_locals
        setattr(cls, 'client', frame_locals.get("self"))
        return function(cls, *args, **kwargs)

    return wrapper
