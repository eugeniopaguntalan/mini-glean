"""
Custom Exceptions
Domain-specific exceptions for the MiniGlean application
"""


class DocumentNotFoundError(Exception):
    """Raised when a document ID doesn't exist"""
    pass


class DocumentLimitExceededError(Exception):
    """Raised when attempting to create more than max allowed documents"""
    pass


class InvalidFileTypeError(Exception):
    """Raised when uploaded file is not the expected type"""
    pass


class FileTooLargeError(Exception):
    """Raised when file exceeds size limit"""
    pass


class PageLimitExceededError(Exception):
    """Raised when PDF has more pages than allowed"""
    pass


class ParseError(Exception):
    """Raised when content parsing fails"""
    pass


class EmbeddingError(Exception):
    """Raised when OpenAI embedding call fails"""
    pass
