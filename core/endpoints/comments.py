"""
Comments endpoints
    1. POST /
    2. GET /<comment_id>
    3. PATCH /<comment_id>
    4. DELETE /<comment_id>
"""


# Imports
from flask import Blueprint, Response
from pydantic import ValidationError
from werkzeug.exceptions import NotFound, Forbidden
from core.models import Comment
from ..decorators import json_required, bearer_required
from ..validation import helpers, schemas
from .. import db


# Blueprint
comments = Blueprint(name="comments", import_name=__name__, url_prefix="/comments")


# Routes
@comments.route("<comment_id>", methods=["GET"])
@bearer_required
def view(user, comment_id):
    """ View comment """

    # Find comment in DB
    comment = Comment.find_by_uid(comment_id)
    if not comment:
        raise NotFound(description="comment not found")

    return comment.public_info(user)


@comments.route("<comment_id>", methods=["PATCH"])
@bearer_required
@json_required
def update(data, user, comment_id):
    """ Update comment """

    # Find comment in DB
    comment = Comment.find_by_uid(comment_id)
    if not comment:
        raise NotFound(description="comment not found")

    # Verify comment is user-owned
    try:
        assert comment.owner is user
    except AssertionError:
        raise Forbidden(description="forbidden")

    # Validate comment schema
    try:
        parsed = schemas.UpdateComment(**data)
    except ValidationError as e:
        return helpers.errors_to_response(e.errors())

    # Update comment in DB
    comment.update(parsed.content)
    db.session.commit()

    return comment.public_info(user)


@comments.route("<comment_id>", methods=["DELETE"])
@bearer_required
def delete(user, comment_id):
    """ Delete comment """

    # Find comment in DB
    comment = Comment.find_by_uid(comment_id)
    if not comment:
        raise NotFound(description="comment not found")

    # Verify comment belongs to current user
    try:
        assert comment.owner is user
    except AssertionError:
        raise Forbidden(description="forbidden")

    # delete comment from DB
    comment.delete()
    db.session.commit()
    
    return Response(status=200)