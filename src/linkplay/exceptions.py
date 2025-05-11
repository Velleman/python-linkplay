class LinkPlayException(Exception):
    pass


class LinkPlayRequestException(LinkPlayException):
    pass


class LinkPlayInvalidDataException(LinkPlayException):
    def __init__(self, message: str = "Invalid data received", data: str | None = None):
        super().__init__(message)
        self.data = data
