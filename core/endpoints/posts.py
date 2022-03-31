"""
Posts endpoints
    1. POST /
    2. GET /
    3. GET /<post_id>
    4. PATCH /<post_id>
    5. DELETE /<post_id>
"""


# Imports
from flask import Blueprint, Response, jsonify, request
from pydantic import ValidationError
from ..decorators import bearer_required, json_required, pagination_required
from werkzeug.exceptions import NotFound, Forbidden
from ..validation import schemas, helpers
from ..models import Comment, Post
from .. import db

# Blueprint
posts = Blueprint(name="posts", import_name=__name__, url_prefix="/posts")


# Routes
@posts.route("", methods=["POST"])
@json_required
@bearer_required
def create(user, data):
    """ Create a new Post """

    # Validate post schema
    try:
        parsed = schemas.CreatePost(**data)
    except ValidationError as e:
        return helpers.errors_to_response(e.errors())

    # Create a new post
    new_post = Post.create(user, parsed.content)
    db.session.commit()

    # Return new post info
    return new_post.public_info(user), 201


@posts.route("", methods=["GET"])
@bearer_required
@pagination_required
def get_all(offset, limit, user):
    """ Fetch all posts """
    
    result = list()

    posts = Post.get_all(offset, limit)
    for p in posts:
        result.append(p.public_info(user))

    return jsonify(result)


@posts.route("<post_id>", methods=["GET"])
@bearer_required
def view(user, post_id):
    """ Get post by UID """

    # Search for post in DB
    post = Post.find_by_uid(post_id)
    if not post:
        raise NotFound(description="post not found")

    # Return post info
    return post.public_info(user)

@posts.route("<post_id>", methods=["PATCH"])
@bearer_required
@json_required
def update(data, user, post_id):
    """ Update post """

    # Find post in DB
    post = Post.find_by_uid(post_id)
    if not post:
        raise NotFound(description="post not found")

    # Verify post belongs to current user
    try:
        assert post.owner is user
    except AssertionError:
        raise Forbidden(description="forbidden")

    # Validate post schema
    try:
        parsed = schemas.UpdatePost(**data)
    except ValidationError as e:
        return helpers.errors_to_response(e.errors())

    # Update post
    post.update(parsed.content)
    db.session.commit()

    # Return updated post json
    return post.public_info(user)


@posts.route("<post_id>", methods=["DELETE"])
@bearer_required
def delete(user, post_id):
    """ Delete a post """

    # Find post in DB
    post = Post.find_by_uid(post_id)
    if not post:
        raise NotFound(description="post not found")

    # Verify post belongs to current user
    try:
        assert post.owner is user
    except AssertionError:
        raise Forbidden(description="forbidden")

    # delete post from DB
    post.delete()
    db.session.commit()
    
    return Response(status=200)


@posts.route("<post_id>/comments", methods=["POST"])
@bearer_required
@json_required
def comment(data, user, post_id):
    """ Create a new post comment """

    # Fetch post from DB
    post = Post.find_by_uid(post_id)
    if not post:
        raise NotFound(description="post not found")

    # Validate comment schema
    try:
        parsed = schemas.CreateComment(**data)
    except ValidationError as e:
        return helpers.errors_to_response(e.errors())

    # Add new comment to DB
    new_comment = Comment.create(user, post, parsed.content)
    db.session.commit()

    # Return new comment info
    return new_comment.public_info(user), 201


@posts.route("<post_id>/comments", methods=["GET"])
@bearer_required
@pagination_required
def comments(offset, limit, user, post_id):
    """ Get post comments """

    # Fetch post from DB
    post = Post.find_by_uid(post_id)
    if not post:
        raise NotFound(description="post not found")

    # Create an array of post comments
    comments = post.get_comments(offset, limit)
    result = list()
    for c in comments:
        result.append(c.public_info(user))
    
    # Return an array
    return jsonify(result)
