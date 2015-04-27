#! coding=utf-8
"""DigitalOcean APIv2 client module"""
__author__ = "Sriram Velamur<sriram.velamur@gmail.com>"
__all__ = ("DOClient",)

import sys
sys.dont_write_bytecode = True
from json import dumps as json_dumps
from re import compile as re_compile, match as re_match
from ast import literal_eval
from datetime import datetime as dt
from time import mktime, gmtime

import requests

from .base import BaseObject
from .droplet import Droplet, Kernel, Snapshot, Image, DropletSize
from .errors import APIAuthError, InvalidArgumentError, APIError
from .user import DOUser


class DOClient(BaseObject):

    """DigitalOcean APIv2 client"""

    api_calls_left = None
    api_quota_reset_at = None
    user = None

    droplet_url = "".join([
        "https://api.digitalocean.com/v2/",
        "droplets?page=1&per_page=100"
    ])
    images_url = "".join([
        "https://api.digitalocean.com/v2/",
        "images?page=1&per_page=100"
    ])
    sizes_url = "".join([
        "https://api.digitalocean.com/v2/",
        "sizes?page=1&per_page=100"
    ])

    power_onoff_url = "".join([
        "https://api.digitalocean.com/v2/",
        "droplets/%s/actions"
    ])

    userinfo_url = "https://api.digitalocean.com/v2/account"

    droplet_base_url = "https://api.digitalocean.com/v2/droplets/"
    droplet_snapshot_url = "".join([
        droplet_base_url,
        "%s/snapshots?page=1&per_page=100"
    ])
    droplet_kernels_url = "".join([
        droplet_base_url,
        "%s/kernels?page=1&per_page=100"
    ])
    droplet_neighbours_url = "".join([
        droplet_base_url,
        "%s/neighbors"
    ])

    # Metadata

    poweroff_data = json_dumps({
        "type": "power_off"
    })

    poweron_data = json_dumps({
        "type": "power_on"
    })

    powercycle_data = json_dumps({
        "type": "power_cycle"
    })

    def __init__(self, token):
        """DigitalOcean APIv2 client init"""
        self._token = token
        self.droplets = None
        self.user = None
        self.get_droplets()
        self.get_user_information()

    def get_user_information(self):
        """DigitalOcean APIv2 user information helper method"""

        response = self.api_request(url=self.userinfo_url,
                                    return_json=False)

        if not response.status_code == 200:
            raise APIAuthError("Unable to authenticate session")

        payload = response.json().get("account")
        payload.update({
            "droplet_count": len(self.droplets)
        })

        user = DOUser(**payload)
        self.user = user
        return user

    def __repr__(self):
        return "DigitalOcean API Client %s" % self._id

    def __str__(self):
        return "DigitalOcean API Client %s" % self._id

    @property
    def token(self):
        """
        DigitalOcean API client token property.
        Used with request headers as Authorization Bearer
        """
        return self._token

    @property
    def request_headers(self):
        """
        DigitalOcean API client base request headers property.
        Used with all of the DOClient's HTTP requests.
        """
        return {
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % self.token
        }

    def api_request(self, url, method="GET", data=None, return_json=True):
        """
        DigitalOcean API request helper method.
        :param url: REST API url to place a HTTP request to.
        :type  url: basestring
        :param method: HTTP method
        :type  method: basestring
        :param data: HTTP payload
        :type  data: dict<json>
        :param return_json: Specifies reeturn data.
                            If false, returns bare response.
        :type  return_json: bool
        :rtype: dict, requests.models.Response
        """

        if self.api_calls_left is not None and self.api_calls_left < 1:
            raise APIAuthError("Rate limit exceeded.")

        method = method or "GET"
        method = method.lower()
        http_method = getattr(requests, method, None)

        if http_method is None:
            raise InvalidArgumentError("Invalid HTTP method requested")

        kwargs = {
            "url": url,
            "headers": self.request_headers,
        }

        if data:
            if isinstance(data, dict):
                data = json_dumps(data)
            kwargs.update({"data": data})

        response = http_method(**kwargs)

        if response.status_code > 300:
            raise APIAuthError(
                "Unable to fetch data from DigitalOcean API.")

        reset_timestamp = response.headers.get("ratelimit-reset")
        reset_timestamp = float(reset_timestamp)
        reset_timestamp = dt.fromtimestamp(mktime(gmtime(reset_timestamp)))

        self.api_calls_left = response.headers.get("ratelimit-remaining")
        self.api_quota_reset_at = reset_timestamp

        return response.json() if return_json else response

    def get_images(self):
        """
        Get list of images available.
        :raises: APIAuthError
        """
        response = requests.get(url=self.images_url,
                                headers=self.request_headers)

        if response.status_code != 200:
            raise APIAuthError(
                "Unable to fetch data from DigitalOcean API.")

        images = response.json().get("images")
        return [Image(**image) for image in images]

    def get_sizes(self):
        """
        Get list of image sizes available.
        :raises: APIAuthError
        """
        response = requests.get(url=self.sizes_url,
                                headers=self.request_headers)

        if response.status_code != 200:
            raise APIAuthError(
                "Unable to fetch data from DigitalOcean API.")

        sizes = response.json().get("sizes")
        return [DropletSize(**size) for size in sizes]

    def get_droplets(self):
        """
        Get list of droplets for the requested account.
        :raises: APIAuthError
        """

        response = self.api_request(url=self.droplet_url)

        droplets = response.get("droplets", [])
        _droplets = []

        for droplet in droplets:
            droplet = Droplet(**{
                "name": droplet.get("name"),
                "_id": droplet.get("id"),
                "client": self
            })
            _droplets.append(droplet)

        self.droplets = _droplets

    def poweroff_droplet(self, instance_id):
        """
        Instance power off helper method.
        :param instance_id: ID of the instance to turn off.
        :type  instance_id: int, basestring<int>
        :rtype: dict
        """
        url = self.power_onoff_url % instance_id
        response = requests.post(url=url,
                                 headers=self.request_headers,
                                 data=self.poweroff_data)
        if response.status_code in (401, 403):
            raise APIAuthError("Not authorized to power off droplet")

        return {"message": "Initiated droplet poweroff"}

    def poweron_droplet(self, instance_id):
        """
        Instance power on helper method.
        :param instance_id: ID of the instance to turn on.
        :type  instance_id: int, basestring<int>
        :rtype: dict
        """
        url = self.power_onoff_url % instance_id
        response = requests.post(url=url,
                                 headers=self.request_headers,
                                 data=self.poweron_data)

        if response.status_code in (401, 403):
            raise APIAuthError("Not authorized to power on droplet")

        return {"message": "Initiated droplet poweron"}

    def powercycle_droplet(self, instance_id):
        """
        Instance power cycle helper method.
        :param instance_id: ID of the instance to powercycle.
        :type  instance_id: int, basestring<int>
        :rtype: dict
        """
        url = self.power_onoff_url % instance_id
        response = requests.post(url=url,
                                 headers=self.request_headers,
                                 data=self.poweron_data)

        if response.status_code in (401, 403):
            raise APIAuthError("Not authorized to power cycle droplet")

        return {"message": "Initiated droplet powercycle"}

    def get_droplet(self, droplet_id):
        """
        Basic droplet find helper.
        Filters out droplets which match the provided droplet id.
        [Essentially one droplet].
        :param droplet_id: ID to match droplets against.
        :type  matcher: int, basestring
        :rtype: list<Droplet>
        """

        if not isinstance(droplet_id, int):
            droplet_id = droplet_id or ""
            try:
                droplet_id = literal_eval(str(droplet_id))
            except (TypeError, ValueError):
                droplet_id = None

        if not isinstance(droplet_id, int):
            raise InvalidArgumentError(
                "Method requires a valid integer droplet id")

        droplet = [x for x in self.droplets if x.id == droplet_id]
        return droplet[0] if droplet else None

    def filter_droplets(self, matcher=None):
        """
        Basic droplet filter helper.
        Filters out droplets which pass a substring match on the name
        for the provided matcher.
        Matcher defaults to empty string and returns all instances
        :param matcher: Token to match droplet names against.
        :type  matcher: basestring
        :rtype: list<Droplet>
        """
        if matcher is None:
            return self.droplets

        if not isinstance(matcher, basestring):
            raise InvalidArgumentError(
                "Method requires a string filter token")

        matcher = re_compile(".*?%s.*?" % matcher)
        return [x for x in self.droplets
                if re_match(matcher, x.name) is not None]

    def get_droplet_snapshots(self, droplet_id):
        """
        DigitalOcean APIv2 droplet snapshots helper method.
        Returns a list of snapshots created for the requested droplet.
        :param droplet_id: ID of droplet to get snapshots for.
        :type  droplet_id: int
        :rtype: list<dict>
        """
        url = self.droplet_snapshot_url % droplet_id
        response = requests.get(url=url,
                                headers=self.request_headers)
        if response.status_code != 200:
            raise APIAuthError("Invalid authorization bearer")

        snapshots = response.json().get("snapshots")
        return [Snapshot(**snapshot) for snapshot in snapshots]

    def get_droplet_kernels(self, droplet_id):
        """
        DigitalOcean APIv2 droplet kernels helper method.
        Returns a list of kernels available for the requested droplet.
        :param droplet_id: ID of droplet to get available kernels for.
        :type  droplet_id: int
        :rtype: list<doclient.droplet.Kernel>
        """
        url = self.droplet_kernels_url % droplet_id
        response = requests.get(url=url,
                                headers=self.request_headers)
        if response.status_code != 200:
            raise APIAuthError("Invalid authorization bearer")

        kernels = response.json().get("kernels")
        return [Kernel(**kernel) for kernel in kernels]

    def get_droplet_neighbours(self, droplet_id):
        """
        DigitalOcean APIv2 droplet neighbours helper method.
        Returns a list of droplets running on the same physical server.
        :param droplet_id: ID of droplet to get neighbours for.
        :type  droplet_id: int
        :rtype: list<doclient.droplet.Droplet>
        """
        url = self.droplet_neighbours_url % droplet_id
        response = requests.get(url=url,
                                headers=self.request_headers)
        if response.status_code != 200:
            raise APIAuthError("Invalid authorization bearer")

        droplets = response.json().get("droplets")
        return [Droplet(**droplet) for droplet in droplets]

    def delete_droplet(self, droplet_id):
        """
        DigitalOcean APIv2 droplet delete method.
        Deletes a requested droplet.
        :param droplet_id: ID of droplet to delete.
        :type  droplet_id: int
        :rtype: dict
        """
        droplet = self.get_droplet(droplet_id)
        if not droplet:
            raise InvalidArgumentError("Unknown droplet")
        url = "%s%s" % (self.droplet_base_url, droplet_id)
        response = requests.delete(url=url,
                                   headers=self.request_headers)
        if response.status_code != 204:
            raise APIAuthError("Invalid authorization bearer")

        return {"message": "Successfully deleted droplet" % droplet}

    def create_droplet(self, name, region, size, image,
                       ssh_keys=None, backups=False, ipv6=False,
                       user_data=None, private_networking=False):
        """
        DigitalOcean APIv2 droplet create method.
        Creates a droplet with requested payload features.
        :param name: Identifier for createddroplet.
        :type  name: basestring
        :param region: Region identifier to spawn droplet
        :type  region: basestring
        :param size: Size of droplet to create.
                     [512mb, 1gb, 2gb, 4gb, 8gb, 16gb, 32gb, 48gb, 64gb]
        :type  size: basestring
        :param image: Name or slug identifier of base image to use.
        :type  image: int, basestring
        :param ssh_keys: SSH keys to add to created droplet
        :type  ssh_keys: list<basestring>, list<long>
        :param backups: Droplet backups enable state parameter
        :type  backups: bool
        :param ipv6: Droplet IPV6 enable state parameter
        :type  ipv6: bool
        :param user_data: User data to be added to droplet's metadata
        :type  user_data: basestring
        :param private_networking: Droplet private networking enable parameter
        :type  private_networking: bool
        :rtype: doclient.droplet.Droplet
        """
        try:
            assert isinstance(name, basestring), \
                "Invalid droplet name. Requires a string name"
            assert isinstance(region, basestring), \
                "Invalid droplet region. Requires a string region id"
            assert isinstance(size, basestring), \
                "Invalid droplet size. Requires a string size"
            assert isinstance(image, (int, long, basestring)), \
                "Invalid base image id. Requires a numeric ID or slug"
            backups = backups if isinstance(backups, bool) else False
            private_networking = private_networking if \
                isinstance(private_networking, bool) else False
            ipv6 = ipv6 if isinstance(ipv6, bool) else False
            user_data = user_data if \
                isinstance(user_data, basestring) else None
            ssh_keys = ssh_keys if isinstance(ssh_keys, list) and \
                all([isinstance(x, (int, long, basestring))
                     for x in ssh_keys]) else False
            payload = json_dumps({
                "name": name,
                "region": region,
                "size": size,
                "image": image,
                "ssh_keys": ssh_keys,
                "backups": backups,
                "private_networking": private_networking,
                "ipv6": ipv6,
                "user_data": user_data,
            })
            response = requests.post(url=self.droplet_base_url,
                                     headers=self.request_headers,
                                     data=payload)

            if response.status_code != 202:
                raise APIError(
                    "Unable to create a droplet with requested data")

            droplet = response.json().get("droplet")
            return Droplet(**droplet)

        except AssertionError, err:
            raise InvalidArgumentError(err)


if __name__ == "__main__":
    pass
