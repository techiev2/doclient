#! coding=utf-8
"""
DigitalOcean APIv2 metadata module
Exposes meta classes for meta informtaion.
"""
__author__ = "Sriram Velamur <sriram.velamur@gmail.com>"
__all__ = ("Domain", "Kernel", "Snapshot")

import sys
sys.dont_write_bytecode = True

from .base import BaseObject
from .helpers import set_caller


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
        elif status != 200:
            message = response.json().get("message")
            raise InvalidArgumentError(message)

        return Domain(**response.json().get("domain"))

    @classmethod
    @set_caller
    def get_all(cls):
        """
        Get all domain maps generated through DigitalOcean's DNS.
        :rtype: list<Domain>
        """
        response = cls.client.api_request(url=cls.base_url,
                                         return_json=False)
        status = response.status_code
        if status in (401, 403):
            raise APIAuthError("Invalid authentication bearer")
        elif status == 400:
            raise InvalidArgumentError("Invalid payload data")
        elif status == 500:
            raise APIError("DigitalOcean API error. Please try later.")
        elif status != 200:
            message = response.json().get("message")
            raise InvalidArgumentError(message)
        domains = response.json().get("domains", [])
        return [Domain(**domain) for domain in domains]

    @classmethod
    @set_caller
    def delete(cls, name):
        """
        Domain mapping delete helper method
        :param name: Domain name
        :type  name: basestring
        :rtype: dict
        """
        url = "%s%s" % (cls.base_url, name)
        response = cls.client.api_request(url=url,
                                          method="delete",
                                          return_json=False)
        status = response.status_code
        if status in (401, 403):
            raise APIAuthError("Invalid authentication bearer")
        elif status == 400:
            raise InvalidArgumentError("Invalid payload data")
        elif status == 500:
            raise APIError("DigitalOcean API error. Please try later.")
        elif status != 204:
            message = response.json().get("message")
            raise InvalidArgumentError(message)

        return {
            "message": "Successfully initiated domain mapping delete"
        }


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


class Region(BaseObject):

    """DigitalOcean region object class"""

    available, sizes, features, name, slug = (None,) * 5

    def __repr__(self):
        return "Region %s {%s - %s}" % \
            (self.name, self.slug,
                "Available" if self.available else "Unavailable")

    def __str__(self):
        return "Region %s {%s - %s}" % \
            (self.name, self.slug,
                "Available" if self.available else "Unavailable")


class SSHKey(BaseObject):

    """SSH key object associated with a DigitalOcean account"""

    fingerprint, name, public_key = None, None, None

    def __repr__(self):
        return "SSH Key %s {%s}" % (self.name, self.fingerprint)

    def __str__(self):
        return "SSH Key %s {%s}" % (self.name, self.fingerprint)
