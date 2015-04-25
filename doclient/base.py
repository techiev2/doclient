#! coding=utf-8
"""DigitalOcean APIv2 base model module"""
__author__ = "Sriram Velamur <sriram.velamur@gmail.com>"
__all__ = ("BaseObject",)

import sys
sys.dont_write_bytecode = True


class BaseObject(object):
    def __init__(self, **kwargs):
        for name, value in kwargs.iteritems():
            setattr(self, name, value)
