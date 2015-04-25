#! coding=utf-8

import sys
sys.dont_write_bytecode = True

from .base import BaseObject


class Droplet(BaseObject):

    """DigitalOcean droplet object"""

    client, name = None, None

    def power_off(self):
        print "Powering off droplet %s" % self.name
        self.client.poweroff_droplet(self.id)

    def power_on(self):
        print "Powering on droplet %s" % self.name
        self.client.poweron_droplet(self.id)

    def power_cycle(self):
        print "Power cycling droplet %s" % self.name
        self.client.powercycle_droplet(self.id)

    def __repr__(self):
        return "Droplet %s <ID: %s>" % (self.name, self.id)

    def __str__(self):
        return "Droplet %s <ID: %s>" % (self.name, self.id)

    def as_dict(self):
        """Returns a dictionary representation of a Droplet"""
        return {"name": self.name, "id": self.id}

    def get_snapshots(self):
        """
        DigitalOcean droplet snapshots list helper.
        Returns a list of snapshots created for a particular droplet.
        :rtype: list<dict>
        """
        return self.client.get_droplet_snapshots(self.id)

    def get_kernels(self):
        """
        DigitalOcean droplet kernels list helper.
        Returns a list of kernels available for a particular droplet.
        :rtype: list<dict>
        """
        return self.client.get_droplet_kernels(self.id)


class Kernel(BaseObject):
    """DigitalOcean droplet kernel object"""

    version, name = None, None

    def __repr__(self):
        return "Kernel %s [Name: %s | Version: %s]" % (
            self.id, self.name, self.version)

    def __str__(self):
        return "Kernel %s [Name: %s | Version: %s]" % (
            self.id, self.name, self.version)


class Snapshot(BaseObject):

    droplet, _id, name, distribution, public = (None,) * 5
    regions, created_at = None, None
    _type, min_disk_size = None, None

    @property
    def type(self):
        return self._type

    def __repr__(self):
        return "Snapshot %s [%s] of droplet %s. Running %s" % \
            (self.id, self.name, self.droplet, self.distribution)

    def __str__(self):
        return "Snapshot %s [%s] of droplet %s. Running %s" % \
            (self.id, self.name, self.droplet, self.distribution)
