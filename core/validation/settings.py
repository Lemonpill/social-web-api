"""
Validation configuration
"""

class Settings(object):
    """
    Parsing and validation constants
    """

    EMAIL_MINLEN = 5
    EMAIL_MAXLEN = 100
    EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

    DISPLAY_NAME_MINLEN = 1
    DISPLAY_NAME_MAXLEN = 50
    DISPLAY_NAME_REGEX = r"^[A-Za-z0-9._-]*$"

    PASS_MINLEN = 8
    PASS_MAXLEN = 2048
    PASS_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&]).*$"

    POST_MINLEN = 1
    POST_MAXLEN = 5000

    COMMENT_MINLEN = 1
    COMMENT_MAXLEN = 1000