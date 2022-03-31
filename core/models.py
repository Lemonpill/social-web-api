"""
ORM for the app DB
"""


# Imports
from datetime import datetime
from flask import request
import shortuuid
import timeago
from werkzeug.security import generate_password_hash
from . import db
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    desc
)


# Functions
def uuid_gen(l):
    """
    generate a cryptographically secure random
    string (using os.urandom() internally)
    """
    return shortuuid.ShortUUID().random(length=l)


# Models
class User(db.Model):
    """ Users table """

    id = Column(Integer, primary_key=True)
    uid = Column(String(16), unique=True)
    email = Column(String(50), unique=True)
    password = Column(String(100))
    display_name = Column(String(50))
    created = Column(DateTime, default=None)
    updated = Column(DateTime, default=None)

    posts = db.relationship("Post", backref="owner", lazy="dynamic", cascade="all, delete")
    comments = db.relationship("Comment", backref="owner", lazy="dynamic", cascade="all, delete")

    @staticmethod
    def find_by_id(id):
        """ Find a user by ID """

        return db.session.query(User).filter_by(id=id).first()

    @staticmethod
    def find_by_uid(uid):
        """ Find a user by UID """

        return db.session.query(User).filter_by(uid=uid).first()

    @staticmethod
    def find_by_email(email):
        """ Find a user by email """
        
        e = email.lower()
        return db.session.query(User).filter_by(email=e).first()
    
    @staticmethod
    def create(email, pwd, display_name):
        """ Create a new user """

        now = datetime.now()
        new = User(
                uid=uuid_gen(16),
                email=email.lower(),
                password=generate_password_hash(pwd, "SHA256"),
                display_name=display_name,
                created=now,
                updated=now
            )
        db.session.add(new)
        return new

    def private_info(self):
        """ Get user private info """

        return {
            "id": self.uid,
            "display_name": self.display_name,
            "email": self.email,
            "created": self.created,
            "updated": self.updated
        }

    def public_info(self):
        """ Get user public info """

        return {
            "id": self.uid,
            "display_name": self.display_name
        }

    def update(self, email, pwd, display_name):
        """ Update user info """

        self.email = email.lower()
        self.password = generate_password_hash(pwd, "SHA256")
        self.display_name = display_name
        self.updated = datetime.now()

    def delete(self):
        """ Delete current row """
        
        db.session.delete(self)

    def get_posts(self, offset=0, limit=20):
        """ Get user posts """

        return self.posts.order_by(desc(Post.created)).offset(offset).limit(limit)

    def get_comments(self, offset=0, limit=20):
        """ Get user comments """

        return self.comments.offset(offset).limit(limit)


class Post(db.Model):
    """ Posts table """

    id = Column(Integer, primary_key=True)
    uid = Column(String(16), unique=True)
    owner_id = Column(Integer, ForeignKey("user.id"))
    content = Column(String(5000))
    created = Column(DateTime, default=None)
    updated = Column(DateTime, default=None)

    comments = db.relationship("Comment", backref="post", lazy="dynamic", cascade="all, delete")

    @staticmethod
    def create(user, content):
        """ Create a new post """

        now = datetime.now()
        new = Post(
            uid=uuid_gen(16),
            owner_id=user.id,
            content=content,
            created=now,
            updated=now
        )
        db.session.add(new)
        return new

    @staticmethod
    def get_all(offset, limit):
        """ Fetch all posts ordered by descending date """

        return db.session.query(Post).order_by(desc(Post.created)).offset(offset).limit(limit)


    def public_info(self, user):
        """ Get post public info """
        
        if self.owner is user:
            actions = ["View", "Edit", "Delete"]
        else:
            actions = ["View"]

        return {
            "id": self.uid,
            "content": self.content,
            "created": timeago.format(datetime.now() - self.created),
            "updated": self.updated,
            "comments": self.comments.count(),
            "owner": {
                "id": self.owner.uid,
                "display_name": self.owner.display_name
            },
            "actions": actions
        }

    def short_info(self, user):
        """ Get post short info """

        if self.owner is user:
            actions = ["View", "Edit", "Delete"]
        else:
            actions = ["View"]

        return {
            "id": self.uid,
            "content": self.trimmed_content(),
            "created": timeago.format(datetime.now() - self.created),
            "updated": self.updated,
            "comments": self.comments.count(),
            "href": f"{request.base_url}/{self.uid}",
            "owner": {
                "id": self.owner.uid,
                "display_name": self.owner.display_name
            },
            "actions": actions
        }

    @staticmethod
    def find_by_uid(uid):
        """ Get a post by UID """

        return db.session.query(Post).filter_by(uid=uid).first()

    def update(self, content):
        """ Update current row """

        self.content = content
        self.updated = datetime.now()

    def delete(self):
        """ Delete current row """
        
        db.session.delete(self)

    def get_comments(self, offset=0, limit=20):
        """ Fetch current post comments """

        return self.comments.order_by(desc(Comment.created)).offset(offset).limit(limit)

    def get_comments_count(self):
        """ Get current post comment count """

        return self.comments.count()

    def trimmed_content(self, n=150):
        """
        Get post content trimmed to n characters,
        Truncate the rest with '...'
        """

        return self.content if len(self.content) <= n else self.content[:250] + "..."




class Comment(db.Model):
    """ Comments table """

    id = Column(Integer, primary_key=True)
    uid = Column(String(16), unique=True)
    owner_id = Column(Integer, ForeignKey("user.id"))
    post_id = Column(Integer, ForeignKey("post.id"))
    content = Column(String(1000))
    created = Column(DateTime, default=None)
    updated = Column(DateTime, default=None)


    @staticmethod
    def find_by_uid(uid):
        """ Find a comment by UID """

        return db.session.query(Comment).filter_by(uid=uid).first()
    
    @staticmethod
    def create(user, post, content):
        """ Create a new Comment """

        now = datetime.now()
        new = Comment(
            uid=uuid_gen(16),
            owner_id=user.id,
            post_id=post.id,
            content=content,
            created=now,
            updated=now
        )
        db.session.add(new)
        return new

    def public_info(self, user):
        """ Get comment public info """

        if self.owner is user:
            actions = ["View", "Edit", "Delete"]
        else:
            actions = ["View"]

        return {
            "id": self.uid,
            "content": self.content,
            "created": timeago.format(datetime.now() - self.created),
            "updated": self.updated,
            "owner": {
                "id": self.owner.uid,
                "display_name": self.owner.display_name
            },
            "post_id": self.post.uid,
            "actions": actions
        }

    def update(self, content):
        """ Update an existing comment """

        self.content = content
        self.updated = datetime.now()

    def delete(self):
        """ Delete current row """

        db.session.delete(self)