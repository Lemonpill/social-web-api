"""
Endpoint decorators
"""


# Imports
from werkzeug.exceptions import BadRequest, Unauthorized
from functools import wraps
from flask import request
from jwt.exceptions import PyJWTError
from . import app
from .models import User
import jwt


# Decorators
def decorator_boilerplate(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data = None
        return f(data, *args, **kwargs)
    return decorated

def json_required(f):
    """
    Verifies request contains a valid json
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        data = None
        
        # Validate request content-type
        try:
            assert request.is_json
        except AssertionError:
            raise BadRequest(description="content-type must be application/json")
        
        # Save request json body
        try:
            data = request.get_json()
        except Exception:
            raise BadRequest(description="invalid json format")
        
        # Verify json is an instance of dictionary
        try:
            assert isinstance(data, dict)
        except AssertionError:
            raise BadRequest(description="invalid json format")

        # Return json data
        return f(data, *args, **kwargs)
    return decorated

def bearer_required(f) -> User:
    """
    1. Verifies request header contains authorization token (type 'access')
    2. Decodes the bearer and returns the relevant user
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Verify authorization headers
        try:
            assert "Authorization" in request.headers
        except AssertionError:
            raise Unauthorized(description="authentication is required")

        # Get token from headers
        token = request.headers["Authorization"][7:]

        # Decode token
        try:
            decoded = jwt.decode(jwt=token, key=app.secret_key, algorithms=["HS256"])
        except PyJWTError:
            raise Unauthorized(description="could not authenticate")
        
        # Verify token scope
        try:
            assert decoded["scp"] == "access"
        except AssertionError:
            raise Unauthorized(description="could not authenticate")
        
        # Find the relevant user in DB
        user = User.find_by_uid(decoded["uid"])
        if not user:
            raise Unauthorized(description="could not authenticate")
        
        # Return user
        return f(user, *args, **kwargs)
    return decorated

def refresh_required(f) -> User:
    """
    1. Verifies request header contains authorization token (type 'refresh')
    2. Decodes the bearer and returns the relevant user
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Verify authorization headers
        try:
            assert "Authorization" in request.headers
        except AssertionError:
            raise Unauthorized(description="authentication is required")
        
        # Get token from headers
        token = request.headers["Authorization"][7:]

        # Decode token
        try:
            decoded = jwt.decode(jwt=token, key=app.secret_key, algorithms=["HS256"])
        except PyJWTError:
            raise Unauthorized(description="could not authenticate")

        # Verify token scope
        try:
            assert decoded["scp"] == "refresh"
        except AssertionError:
            raise Unauthorized(description="could not authenticate")

        # Find the relevant user in DB
        user = User.find_by_uid(decoded["uid"])
        if not user:
            raise Unauthorized(description="could not authenticate")
        
        # Return user
        return f(user, *args, **kwargs)
    return decorated

def pagination_required(f):
    """ 
    Verifies request params contain a valid offset and a limit
    In case those are missing, offset defaults to 0 and limit defaults to 100
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get offset and limit request parameters
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        # If offset is False, default to 0
        if not offset:
            offset = 0

        # If limit is False, default to 20
        if not limit:
            limit = 20

        # Convert offset to integer
        errors = dict()
    
        try:
            offset = int(offset)
        except ValueError:
            errors["offset"] = "offset must be an integer"
        
        # Convert limit to integer
        try:
            limit = int(limit)
        except ValueError:
            errors["limit"] = "limit must be an integer"

        # Return errors if found
        if errors:
            return {
                "message": "validation error",
                "errors": errors
            }, 400

        # Default offset to 0 if negative
        if offset < 0:
            offset = 0

        # Default limit to 20 if negative or too big
        if limit <= 0 or limit > 20:
            limit = 20
        
        # Return offset and limit
        return f(offset, limit, *args, **kwargs)
    return decorated