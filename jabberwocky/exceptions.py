class JabberwockyException(Exception):
    pass


class UpdateException(JabberwockyException):
    pass


class CreationException(JabberwockyException):
    pass


class RemoveException(JabberwockyException):
    pass


class ReloadException(JabberwockyException):
    pass


class ResetException(JabberwockyException):
    pass


class LogoutException(JabberwockyException):
    pass


class NotAttachedException(JabberwockyException):
    pass


class ProtocolException(JabberwockyException):
    pass