#! coding=utf-8
"""DigitalOcean APIv2 client errors module"""
__author__ = "Sriram Velamur<sriram.velamur@gmail.com>"
__all__ = ("APIAuthError", "InvalidArgumentError", "APIError")

import sys
sys.dont_write_bytecode = True


class APIAuthError(BaseException):
    """
    DigitalOcean APIv2 authentication error class.
    Raised when client initialization receives a HTTP 401 while
    requesting for list of instances associated with the account.
    """

    def __init__(self, *args, **kwargs):
        if not args:
            raise RuntimeError("Invalid invocation")
        message = args[0]
        message = "DOClient::APIError: %s" % message
        args = (message,)
        super(APIAuthError, self).__init__(*args, **kwargs)


class InvalidArgumentError(BaseException):
    """
    DigitalOcean APIv2 method arugment error class.
    Raised when a method receives an invalid, empty,
    or type mismatching value for an arugment.
    """

    def __init__(self, *args, **kwargs):
        if not args:
            raise RuntimeError("Invalid invocation")
        message = args[0]
        message = "DOClient::InvalidArgumentError: %s" % message
        args = (message,)
        super(InvalidArgumentError, self).__init__(*args, **kwargs)


class APIError(BaseException):
    """
    DigitalOcean APIv2 generic API error class.
    Raised when a failure response is received from the
    API that is not an authentication related one.
    """

    def __init__(self, *args, **kwargs):
        if not args:
            raise RuntimeError("Invalid invocation")
        message = args[0]
        message = "DOClient::APIError: %s" % message
        args = (message,)
        super(APIError, self).__init__(*args, **kwargs)
