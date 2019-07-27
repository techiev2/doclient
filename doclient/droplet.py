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
from time import sleep

from .base import BaseObject
from .meta import Snapshot
from .errors import InvalidArgumentError, APIError


class Droplet(BaseObject):
    r"""DigitalOcean droplet object"""

    client, name, ipv4_ip, ipv6_ip = (None,) * 4
    networks = []

    droplet_base_url = 'https://api.digitalocean.com/v2/droplets/'
    droplet_snapshot_url = '{}/snapshots?page=1&per_page=100'.format(
        droplet_base_url
    )
    droplet_neighbours_url = '{}/neighbors'.format(droplet_base_url)
    droplet_actions_url = "{0}{1}/actions"

    def power_off(self):
        """Droplet power off helper method"""
        print("Powering off droplet {0}".format(self.name))
        self.client.poweroff_droplet(self.id)

    def power_on(self):
        """Droplet power on helper method"""
        print("Powering on droplet {0}".format(self.name))
        self.client.poweron_droplet(self.id)

    def power_cycle(self):
        """Droplet power cycle helper method"""
        print("Power cycling droplet {0}".format(self.name))
        self.client.powercycle_droplet(self.id)

    def __repr__(self):
        return "Droplet {0} [ID: {1}]".format(self.name, self.id)

    def __str__(self):
        return "Droplet {0} [ID: {1}]".format(self.name, self.id)

    def as_dict(self):
        """Returns a dictionary representation of a Droplet"""
        return {"name": self.name, "id": self.id}

    def get_kernels(self):
        r"""
        DigitalOcean droplet kernels list helper.
        Returns a list of kernels available for a particular droplet.

        :rtype: list (:class:`Kernel <doclient.meta.Kernel>`)
        """
        return self.client.get_droplet_kernels(self.id)

    def get_neighbours(self):
        r"""
        DigitalOcean APIv2 droplet neighbours helper method.
        Returns a list of droplets running
        on the same physical server.

        :rtype: list (:class:`Droplet <.Droplet>`)
        """
        url = self.droplet_neighbours_url.format(self.id)
        response = self.client.api_request(url=url)
        droplets = response.get("droplets", [])
        return [Droplet(**droplet) for droplet in droplets]

    def delete(self):
        r"""
        DigitalOcean droplet delete helper. Deletes a particular droplet.

        :rtype: dict
        """
        return self.client.delete_droplet(self.id)

    def get_snapshots(self):
        r"""
        DigitalOcean droplet snapshot list helper.
        Returns a list of snapshots for a particular droplet.

        :rtype: list (:class:`Snapshot <doclient.meta.Snapshot>`)
        """
        url = self.droplet_snapshot_url % self.id
        response = self.client.api_request(url=url, return_json=True)
        snapshots = response.get("snapshots")
        return [Snapshot(**snapshot) for snapshot in snapshots]

    def reset_password(self):
        r"""
        DigitalOcean droplet access password reset helper method.
        Initializes a password reset for a requested droplet.
        """
        url = self.droplet_actions_url.format(
            self.droplet_base_url, self.id)
        print("Attempting to reset password for droplet {0}".format(
            self.id
        ))
        payload = {
            "type": "password_reset"
        }
        self.client.api_request(url=url, data=payload)

    def resize(self, new_size, disk_resize=False):
        r"""
        Digitalocean droplet resize helper method

        :param new_size: New droplet size to be resized to.
        :type  new_size: str
        :param disk_resize: Boolean to indicate disk resizing.
        :type  disk_resize: bool
        :return: Resized current droplet object.

        :rtype: :class:`Droplet <.Droplet>`
        """
        url = self.droplet_actions_url.format(
            self.droplet_base_url, self.id)
        print("".join([
            "Droplet {0} needs to be powered off before resize.",
            " Caveat emptor: Please power on the droplet",
            " via the Digitalocean console or the API after "
            "resizing."]).format(self.id))
        self.power_off()
        # Wait for 30 seconds to allow for the droplet to power off
        # before inititalizing the resizing. This, and the sleep after
        # resizing, are arbitrary values.
        # TODO: Use information from the API on the droplet status and
        # use event triggers/similar to initialize further changes.
        sleep(30)

        if not isinstance(new_size, str):
            raise InvalidArgumentError(
                "Invalid size specified. Required a valid string "
                "size representation")
        # TODO: Move to meta module as a global.
        # 01-17-2018 - The hardcoded list breaks any future changes
        # to the sizes. Find a way to better cache this information
        # with minimal API call load.
        # This change type needs to be incorporated for other meta
        # information like zones/images too.
        # valid_sizes = ("512mb", "1gb", "2gb", "4gb", "8gb", "16gb",
        #                "32gb", "48gb", "64gb")
        # if new_size not in valid_sizes:
        #     raise InvalidArgumentError(
        #         "Invalid size specified. Size must be an available "
        #         "size in {0}".format("".join(valid_sizes)))
        if not isinstance(disk_resize, bool):
            disk_resize = False

        resize_payload = {
            "type": "resize",
            "disk": disk_resize,
            "size": new_size
        }

        response = self.client.api_request(
            url=url, method="post", data=resize_payload)

        # Handle errors
        if response.get("message"):
            raise APIError(response.get("message"))

        # Wait for 30 seconds after resizing to power on the droplet
        # for usual use. Refer TODO above for the caveat of arbitrary
        # sleep duration.
        sleep(30)
        self.power_on()

        return self.client.filter_droplets(self.id)


class Image(BaseObject):

    """
    DigitalOcean droplet base image object

    :property min_disk_size: Minimum disk size for the image.

    :property slug: Slug identifier for the image.

    :property name: Human readable identifier name for the image.

    :property _id: Identifier for the image.

    :property regions: Regions the image is available in.

    """

    min_disk_size, slug, name, _id, regions = (None,) * 5

    def __repr__(self):
        return "Image {0} [{1}]".format(self.id, self.name)

    def __str__(self):
        return "Image {0} [{1}]".format(self.id, self.name)


class DropletSize(BaseObject):

    """DigitalOcean droplet size repr object"""

    price_monthly, price_hourly, memory, disk, slug = (None,) * 5
    regions, transfer, available, vcplus = (None,) * 4

    def __repr__(self):
        available = "Available" if self.available else "Not available"
        return "Size {0} [{1}]".format(self.slug, available)

    def __str__(self):
        available = "Available" if self.available else "Not available"
        return "Size {0} [{1}]".format(self.slug, available)
