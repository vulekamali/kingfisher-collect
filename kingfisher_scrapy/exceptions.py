class KingfisherScrapyError(Exception):
    """Base class for exceptions from within this application"""


class AuthenticationError(KingfisherScrapyError):
    """Raised when the maximum number of attempts to retrieve an access token is reached"""


class SpiderArgumentError(KingfisherScrapyError):
    """Raised when a spider argument's value is invalid"""


class MissingNextLinkError(KingfisherScrapyError):
    """Raised when a next link is not found on the first page of results"""
