#! coding=utf-8

import sys
sys.dont_write_bytecode = True

from .base import BaseObject


class Droplet(BaseObject):

    """DigitalOcean droplet object"""

    client, _id, name = (None,) * 3

    def power_off(self):
        print "Powering off droplet %s" % self.name
        self.client.poweroff_droplet(self._id)

    def power_on(self):
        print "Powering on droplet %s" % self.name
        self.client.poweron_droplet(self._id)

    def power_cycle(self):
        print "Power cycling droplet %s" % self.name
        self.client.powercycle_droplet(self._id)

    def __repr__(self):
        return "Droplet %s <ID: %s>" % (self.name, self._id)

    def __str__(self):
        return "Droplet %s <ID: %s>" % (self.name, self._id)

    def as_dict(self):
        """Returns a dictionary representation of a Droplet"""
        return {"name": self.name, "id": self._id}

    def get_snapshots(self):
        """
        DigitalOcean droplet snapshots list helper.
        Returns a list of snapshots created for a particular droplet.
        :rtype: list<dict>
        """
        return self.client.get_droplet_snapshots(self._id)

    def get_kernels(self):
        """
        DigitalOcean droplet kernels list helper.
        Returns a list of kernels available for a particular droplet.
        :rtype: list<dict>
        """
        return self.client.get_droplet_kernels(self._id)


class Kernel(BaseObject):
    """DigitalOcean droplet kernel object"""

    version, id, name = (None,) * 3

    def __repr__(self):
        return "Kernel %s [Name: %s | Version: %s]" % (
            self.id, self.name, self.version)

    def __str__(self):
        return "Kernel %s [Name: %s | Version: %s]" % (
            self.id, self.name, self.version)
