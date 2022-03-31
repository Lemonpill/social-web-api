"""
Validation schemas
"""


# Imports
from pydantic import BaseModel, Field
from .settings import Settings as s


# Schemas
class NewUser(BaseModel):
    """
    Parse and validate user create schema
    """
    email: str = Field(
        ..., # is required
        min_length=s.EMAIL_MINLEN,
        max_length=s.EMAIL_MAXLEN,
        regex=s.EMAIL_REGEX
        )
    password: str = Field(
        ..., # is required
        min_length=s.PASS_MINLEN,
        max_length=s.PASS_MAXLEN,
        regex=s.PASS_REGEX
        )
    display_name: str = Field(
        ..., # is required
        min_length=s.DISPLAY_NAME_MINLEN,
        max_length=s.DISPLAY_NAME_MAXLEN,
        regex=s.DISPLAY_NAME_REGEX
        )

class UpdateUser(BaseModel):
    """
    Parse and validate user update schema
    """
    email: str = Field(
        ..., # is required
        min_length=s.EMAIL_MINLEN,
        max_length=s.EMAIL_MAXLEN,
        regex=s.EMAIL_REGEX
        )
    password: str = Field(
        ..., # is required
        min_length=s.PASS_MINLEN,
        max_length=s.PASS_MAXLEN,
        regex=s.PASS_REGEX
        )
    display_name: str = Field(
        ..., # is required
        min_length=s.DISPLAY_NAME_MINLEN,
        max_length=s.DISPLAY_NAME_MAXLEN,
        regex=s.DISPLAY_NAME_REGEX
        )

class CreatePost(BaseModel):
    """ Parse and validate create post schema """

    content: str = Field(
        ..., # is required
        min_length=s.POST_MINLEN,
        max_length=s.POST_MAXLEN
        )

class UpdatePost(BaseModel):
    """ Parse and validate update post schema """

    content: str = Field(
        ..., # is required
        min_length=s.POST_MINLEN,
        max_length=s.POST_MAXLEN
        )

class CreateComment(BaseModel):
    """ Parse and validate create comment schema """

    content: str = Field(
        ..., # is required
        min_length=s.COMMENT_MINLEN,
        max_length=s.COMMENT_MAXLEN
        )

class UpdateComment(BaseModel):
    """ Parse and validate update comment schema """

    content: str = Field(
        ..., # is required
        min_length=s.COMMENT_MINLEN,
        max_length=s.COMMENT_MAXLEN
        )