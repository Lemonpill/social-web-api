"""
Users endpoints
    1. GET /<uid>
    2. GET /me
    3. PATCH /me
    4. DELETE /me
"""


# Imports
from flask import Blueprint, Response, jsonify
from pydantic import ValidationError
from werkzeug.exceptions import NotFound
from ..decorators import bearer_required, json_required, pagination_required
from ..models import User
from ..validation import schemas, helpers
from .. import db


# Blueprint
users = Blueprint(name="users", import_name=__name__, url_prefix="/users")


# Routes
@users.route("<user_id>", methods=["GET"])
@bearer_required
def public_profile(user, user_id):
    """ Get user's public profile """

    # Find user by uid
    u = User.find_by_uid(user_id)
    if not u:
        raise NotFound(description="user not found")
    
    # Return user info
    return u.public_info()


@users.route("<user_id>/posts", methods=["GET"])
@bearer_required
@pagination_required
def user_posts(offset, limit, user, user_id):
    """ Get posts by user UID """

   # Find user by uid
    u = User.find_by_uid(user_id)
    if not u:
        raise NotFound(description="user not found")

    # Create an array of user posts
    posts = u.get_posts(offset, limit)
    result = list()
    for p in posts:
        result.append(p.public_info())
    
    # Return an array
    return jsonify(result)


@users.route("<user_id>/comments", methods=["GET"])
@bearer_required
@pagination_required
def user_comments(offset, limit, user, user_id):
    """ Get comments by user UID """

   # Find user by uid
    u = User.find_by_uid(user_id)
    if not u:
        raise NotFound(description="user not found")

    # Create an array of user comments
    comments = u.get_comments(offset, limit)
    result = list()
    for c in comments:
        result.append(c.public_info())
    
    # Return an array
    return jsonify(result)

@users.route("me", methods=["GET"])
@bearer_required
def my_profile(user):
    """ Get my profile """
    
    # Return current user private profile
    return user.private_info()

@users.route("me", methods=["PATCH"])
@json_required
@bearer_required
def update(user, data):
    """ Update current user info """
    
    # Parse and validate new details
    try:
        parsed = schemas.UpdateUser(**data)
    except ValidationError as e:
        return helpers.errors_to_response(e.errors())

    # Verify email is not taken
    try:
        assert not User.find_by_email(parsed.email)
    except AssertionError:
        return {
            "message": "validation error",
            "errors": {
                "email": "email is taken"
            }
        }, 400

    # Update user details
    user.update(
        email=parsed.email,
        pwd=parsed.password,
        display_name=parsed.display_name,
    )
    db.session.commit()

    # Return new user info
    return user.private_info()


@users.route("me", methods=["DELETE"])
@bearer_required
def delete(user):
    """ Delete current user """

    # Delete user
    user.delete()
    db.session.commit()

    # Return a response
    return Response(status=200)
