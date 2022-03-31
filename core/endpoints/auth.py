"""
Auth endpoints
    1. POST /signup
    2. POST /token
    3. POST /refresh
"""


# Imports
from flask import Blueprint, current_app
from pydantic import ValidationError
from ..decorators import json_required, refresh_required
from ..validation import schemas, helpers
from ..models import User
from .. import db
from werkzeug.exceptions import BadRequest, Unauthorized
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
import jwt


# Blueprint
auth = Blueprint(name="auth", import_name=__name__, url_prefix="/auth")


# Routes
@auth.route("signup", methods=["POST"])
@json_required
def signup(data):
    """ Create a new user """

    # Validate new credentials
    try:
        parsed = schemas.NewUser(**data)
    except ValidationError as e:
        return helpers.errors_to_response(e.errors())

    # Verify email is not taken
    existing_email = User.find_by_email(parsed.email)
    if existing_email:
        return {
            "message": "validation error",
            "errors": {"email": "email is taken"}
        }, 400

    # Add new user to DB
    new_user = User.create(
        parsed.email,
        parsed.password,
        parsed.display_name
    )

    db.session.commit()

    # Return new user data
    return new_user.private_info(), 201


@auth.route("token", methods=["POST"])
@json_required
def token(data):
    """ Create bearer + refresh tokens """
    
    errors = dict()
    
    # Verify email has been provided
    try:
        assert "email" in data.keys()
    except AssertionError:
        errors["email"] = "email is required"
    
    # Verify password has been provided
    try:
        assert "password" in data.keys()
    except AssertionError:
        errors["password"] = "password is required"

    # Return errors in case they exist have been found
    if errors:
        return {
            "message": "validation error",
            "errors": errors
        }, 400
    
    # Verify user exists in DB
    user = User.find_by_email(data["email"])
    try:
        assert user
    except AssertionError:
        raise BadRequest(description="user not found")

    # Verify password is correct
    try:
        assert check_password_hash(user.password, data["password"])
    except AssertionError:
        raise Unauthorized(description="could not authenticate")

    # Generate new access and refresh tokens
    bearer_exp = timedelta(hours=1)
    refresh_exp = timedelta(days=1)
    bearer = jwt.encode(
        payload={
            "uid": user.uid,
            "exp": datetime.now() + bearer_exp,
            "scp": "access"
        },
        key=current_app.secret_key,
        algorithm="HS256"
    )
    refresh = jwt.encode(
        payload={
            "uid": user.uid,
            "exp": datetime.now() + refresh_exp,
            "scp": "refresh"
        },
        key=current_app.secret_key,
        algorithm="HS256"
    )

    # Return access and refresh tokens
    return {
        "bearer": {
            "token": bearer,
            "expires": int(bearer_exp.total_seconds())
        },
        "refresh": {
            "token": refresh,
            "expires": int(refresh_exp.total_seconds())
        }
    }, 201


@auth.route("refresh", methods=["POST"])
@refresh_required
def refresh(user):
    """ Refresh bearer token """

    # Generate new bearer
    expires = timedelta(hours=1)
    token = jwt.encode(
        payload={
            "uid": user.uid,
            "exp": datetime.now() + expires,
            "scp": "access"
        },
        key=current_app.secret_key,
        algorithm="HS256"
    )

    # Return bearer
    return {
        "token": token,
        "expires": int(expires.total_seconds())
    }, 201