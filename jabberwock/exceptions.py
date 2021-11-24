class JabberwockException(Exception):
    pass


class UpdateException(JabberwockException):
    pass


class CreationException(JabberwockException):
    pass


class RemoveException(JabberwockException):
    pass


class ReloadException(JabberwockException):
    pass


class ResetException(JabberwockException):
    pass


class LogoutException(JabberwockException):
    pass


class NotAttachedException(JabberwockException):
    pass


class ProtocolException(JabberwockException):
    pass
