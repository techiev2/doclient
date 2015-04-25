#! coding=utf-8
"""DigitalOcean APIv2 base model module"""
__author__ = "Sriram Velamur <sriram.velamur@gmail.com>"
__all__ = ("BaseObject",)

import sys
sys.dont_write_bytecode = True


class BaseObject(object):

    _id = None

    def __init__(self, **kwargs):
        for name, value in kwargs.iteritems():
            if name == "id":
                name = "_id"
            setattr(self, name, value)

    @property
    def id(self):
        return getattr(self, "_id")