#! coding=utf-8
"""DigitalOcean APIv2 base model module"""
__author__ = "Sriram Velamur <sriram.velamur@gmail.com>"
__all__ = ("BaseObject",)

import sys
sys.dont_write_bytecode = True
from json import dumps


class BaseObject(object):

    """
    BaseObject class for use with doclient objects.
    Provides base id property and init parameter setter.
    """

    _id = None
    props = []

    def __init__(self, **kwargs):
        """BaseObject class init"""
        for name, value in kwargs.iteritems():
            if name in ("id", "token"):
                name = "_%s" % name
            setattr(self, name, value)
            if name not in self.props:
                self.props.append(name)

    def as_dict(self):
        """Dictionary repr for BaseObject objects"""
        return {k: getattr(self, k, None) for k in self.props}

    def as_json(self):
        """JSON repr method for BaseObject objects"""
        data = self.as_dict()
        _data = {}
        for name, value in data.iteritems():
            if isinstance(value, BaseObject):
                value = value.as_json()
            _data[name] = value
        return dumps(_data)

    def __getattr__(self, key):
        """
        Overridden __getattr__ method to work with id property
        """
        if key == "id":
            return self._id
        else:
            return self.key
