#! coding=utf-8
"""
DigitalOcean APIv2 droplet module.
Provides interface classes to Droplets, Kernels,
Snapshots, Images, and Sizes
"""
__author__ = "Sriram Velamur<sriram.velamur@gmail.com>"
__all__ = ("Droplet", "Image", "DropletSize")

import sys
sys.dont_write_bytecode = True

from .base import BaseObject
from .helpers import set_caller
from .errors import InvalidArgumentError, APIAuthError, APIError


class Droplet(BaseObject):

    """DigitalOcean droplet object"""

    client, name = None, None

    def power_off(self):
        """Droplet power off helper method"""
        print "Powering off droplet %s" % self.name
        self.client.poweroff_droplet(self.id)

    def power_on(self):
        """Droplet power on helper method"""
        print "Powering on droplet %s" % self.name
        self.client.poweron_droplet(self.id)

    def power_cycle(self):
        """Droplet power cycle helper method"""
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
        :rtype: list<doclient.droplet.Kernel>
        """
        return self.client.get_droplet_kernels(self.id)

    def get_neighbours(self):
        """
        DigitalOcean droplet neighbours helper.
        Returns a list of droplets running on the same physical server.
        :rtype: list<doclient.droplet.Droplet>
        """
        return self.client.get_droplet_neighbours(self.id)

    def delete(self):
        """
        DigitalOcean droplet delete helper.
        Deletes a particular droplet.
        :rtype: dict
        """
        return self.client.delete_droplet(self.id)




class Image(BaseObject):

    """DigitalOcean droplet base image object"""

    min_disk_size, slug, name, _id, regions = (None,) * 5

    def __repr__(self):
        return "Image %s [%s]" % (self.id, self.name)

    def __str__(self):
        return "Image %s [%s]" % (self.id, self.name)


class DropletSize(BaseObject):

    """DigitalOcean droplet size repr object"""

    price_monthly, price_hourly, memory, disk, slug = (None,) * 5
    regions, transfer, available, vcplus = (None,) * 4

    def __repr__(self):
        available = "Available" if self.available else "Not available"
        return "Size %s [%s]" % (self.slug, available)

    def __str__(self):
        available = "Available" if self.available else "Not available"
        return "Size %s [%s]" % (self.slug, available)

