#! coding=utf-8
"""
DigitalOcean APIv2 droplet module.
Provides interface classes to Droplets, Kernels,
Snapshots, Images, and Sizes
"""
__author__ = "Sriram Velamur<sriram.velamur@gmail.com>"
__all__ = ("Droplet", "Kernel", "Snapshot", "Image", "DropletSize")

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

    """DigitalOcean droplet snapshot object"""

    droplet, _id, name, distribution, public = (None,) * 5
    regions, created_at = None, None
    _type, min_disk_size = None, None

    @property
    def type(self):
        """Droplet snapshot type property"""
        return self._type

    def __repr__(self):
        return "Snapshot %s [%s] of droplet %s. Running %s" % \
            (self.id, self.name, self.droplet, self.distribution)

    def __str__(self):
        return "Snapshot %s [%s] of droplet %s. Running %s" % \
            (self.id, self.name, self.droplet, self.distribution)


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


class Domain(BaseObject):

    """DigitalOcean droplet domain object"""

    name, ttl, zone_file = (None,) * 3
    base_url = "https://api.digitalocean.com/v2/domains/"

    def __repr__(self):
        return "Domain %s" % self.name

    def __str__(self):
        return "Domain %s" % self.name

    @classmethod
    @set_caller
    def create(cls, name, ip_address):
        """Domain creation helper method"""
        payload = {
            "url": cls.base_url,
            "method": "post",
            "data": {
                "name": name,
                "ip_address": ip_address
            },
            "return_json": False
        }
        response = cls.client.api_request(**payload)
        status = response.status_code
        if status in (401, 403):
            raise APIAuthError("Invalid authentication bearer")
        elif status == 400:
            raise InvalidArgumentError("Invalid payload data")
        elif status == 500:
            raise APIError("DigitalOcean API error. Please try later.")
        elif status != 201:
            message = response.json().get("message")
            raise InvalidArgumentError(message)

        return Domain(**response.json().get("domain"))

    @classmethod
    @set_caller
    def get(cls, name):
        """Domain information fetch helper method"""
        url = "%s%s" % (cls.base_url, name)
        response = cls.client.api_request(url=url, return_json=False)
        status = response.status_code
        if status in (401, 403):
            raise APIAuthError("Invalid authentication bearer")
        elif status == 400:
            raise InvalidArgumentError("Invalid payload data")
        elif status == 500:
            raise APIError("DigitalOcean API error. Please try later.")
        elif status != 201:
            message = response.json().get("message")
            raise InvalidArgumentError(message)

        return Domain(**response.json().get("domain"))
