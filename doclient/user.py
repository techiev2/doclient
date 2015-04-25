#! coding=utf-8
"""DigitalOcean APIv2 user module"""
__author__ = "Sriram Velamur <sriram.velamur@gmail.com>"
__all__ = ("DOUser",)

import sys
sys.dont_write_bytecode = True


class DOUser(object):

    """DigitalOcean user object"""

    email_verified, droplet_limit, uuid, email = (None,) * 4

    def __init__(self, **kwargs):
        """DigitalOcean user object init"""
        for name, value in kwargs.iteritems():
            setattr(self, name, value)

    def __repr__(self):
        return "DigitalOcean User: %s (%s)" % (self.uuid, self.email)

    def __str__(self):
        return "DigitalOcean User: %s (%s)" % (self.uuid, self.email)
