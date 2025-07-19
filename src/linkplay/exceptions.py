"""This module defines custom exceptions for the LinkPlay integration."""


class LinkPlayException(Exception):
    """Base exception for LinkPlay errors."""


class LinkPlayRequestException(LinkPlayException):
    """Exception raised for errors in LinkPlay requests."""


class LinkPlayRequestCancelledException(LinkPlayException):
    """Exception raised when a LinkPlay request is cancelled."""


class LinkPlayInvalidDataException(LinkPlayException):
    """Exception raised for invalid data received from LinkPlay endpoints."""

    def __init__(self, message: str = "Invalid data received", data: str | None = None):
        super().__init__(message)
        self.data = data
