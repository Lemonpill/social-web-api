"""
Handling internal and HTTP exceptions
Returns json in case of an exception, writes to log in case of internal errors
"""


# Imports
from datetime import datetime as dt
from werkzeug.exceptions import HTTPException


# Log writer
LOG = "exceptions.txt"
def log(file, txt):
    """
    Write to a log file of choise
    """

    with open(file, "a") as f:
        f.write(
            f"[{dt.now()} [ERROR] [{txt}]\n"
        )


# Handlers
def handler(e):
    """ General exceptions handler """

    msg_500 = {
        "message": "please try again",
        "error": "internal error"
    }, 500

    # Write to log internal errors
    if isinstance(e, HTTPException):
        if e.code == 500:
            log(LOG, e.original_exception)
            return msg_500
        
        # Return error json
        return {
            "error": e.description,
            "message": "could not complete your request"
        }, e.code
    
    log(LOG, e)
    return msg_500