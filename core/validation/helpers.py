"""
Validation helpers
    errors_to_dict
    errors_to_response
"""

# FUNCTIONS #
def errors_to_dict(errs):
    """
    Generate dictionary from pydantic errors
    """
    errors = dict()
    for e in errs:
        errors[e["loc"][0]] = e["msg"]
    return errors

def errors_to_response(errors):
    """
    Generate response from pydantic errors
    """
    return {
        "message": "validation error",
        "errors": errors_to_dict(errors)
    }, 400, {
        "X-Validation-Error": "Validation error"
    }