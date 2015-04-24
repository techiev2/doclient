#! coding=utf-8
"""DigitalOcean APIv2 client package"""
__author__ = "Sriram Velamur<sriram.velamur@gmail.com>"
__all__ = ("APIAuthError", "DOClient")

import sys
sys.dont_write_bytecode = True

from .errors import APIAuthError
from .client import DOClient