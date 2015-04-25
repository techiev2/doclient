#! coding=utf-8

import sys
sys.dont_write_bytecode = True


class Droplet(object):

    """DigitalOcean droplet object"""

    client, _id, name = (None,) * 3

    def __init__(self, **kwargs):
        for name, value in kwargs.iteritems():
            setattr(self, name, value)

    def power_off(self):
        print "Powering off droplet %s" % self.name
        self.client.poweroff_instance(self._id)

    def power_on(self):
        print "Powering on droplet %s" % self.name
        self.client.poweron_instance(self._id)

    def power_cycle(self):
        print "Power cycling droplet %s" % self.name
        self.client.powercycle_instance(self._id)

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
