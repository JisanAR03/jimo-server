from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, ForeignKey, Table, select, func
from geoalchemy2 import Geography
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, column_property
from sqlalchemy.sql import expression

from app.database import Base

follow = Table("follow", Base.metadata,
               Column("from_user_id", BigInteger, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
               Column("to_user_id", BigInteger, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
               Column("created_at", DateTime(timezone=True), nullable=False))


class User(Base):
    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True, nullable=False)
    email = Column(String(length=255), unique=True, nullable=False)
    username = Column(String(length=255), unique=True, nullable=False)
    first_name = Column(String(length=255), nullable=False)
    last_name = Column(String(length=255), nullable=False)
    profile_picture_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    deactivated = Column(Boolean, nullable=False, server_default=expression.false())

    posts = relationship("Post", back_populates="user", cascade="all, delete", passive_deletes=True)

    following = relationship("User",
                             secondary=follow,
                             primaryjoin=id == follow.c.from_user_id,
                             secondaryjoin=id == follow.c.to_user_id,
                             cascade="all, delete",
                             backref="followers")
    followers = None  # Computed with backref above

    _login_methods = relationship("UserAuthType")
    login_methods = association_proxy("_login_methods", "auth_type")

    # Computed column properties
    post_count = None
    follower_count = None
    following_count = None


class UserAuthType(Base):
    __tablename__ = "user_auth_type"

    id = Column(BigInteger, primary_key=True, nullable=False)
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    auth_type = Column(String, nullable=False)


class Category(Base):
    __tablename__ = "category"

    id = Column(BigInteger, primary_key=True, nullable=False)
    name = Column(String, unique=True, nullable=False)


class Tag(Base):
    __tablename__ = "tag"

    id = Column(BigInteger, primary_key=True, nullable=False)
    name = Column(String, unique=True, nullable=False)


class Place(Base):
    __tablename__ = "place"

    id = Column(BigInteger, primary_key=True, nullable=False)
    urlsafe_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    category_id = Column(BigInteger, ForeignKey("category.id"), nullable=False)
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    apple_place_id = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    category = relationship("Category")
    posts = relationship("Post", back_populates="place")


post_tag = Table("post_tag", Base.metadata,
                 Column("post_id", BigInteger, ForeignKey("post.id", ondelete="CASCADE"), nullable=False),
                 Column("tag_id", BigInteger, ForeignKey("tag.id", ondelete="CASCADE"), nullable=False))

post_like = Table("post_like", Base.metadata,
                  Column("user_id", BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
                  Column("post_id", BigInteger, ForeignKey("post.id", ondelete="CASCADE"), nullable=False),
                  Column("created_at", DateTime(timezone=True), nullable=False))


class Post(Base):
    __tablename__ = "post"

    id = Column(BigInteger, primary_key=True, nullable=False)
    urlsafe_id = Column(String, unique=True, nullable=False)
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    place_id = Column(BigInteger, ForeignKey("place.id"), nullable=False)
    content = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User", back_populates="posts")
    place = relationship("Place", back_populates="posts")
    _tags = relationship("Tag", secondary=post_tag, cascade="all, delete", passive_deletes=True)
    likes = relationship("User", secondary=post_like, cascade="all, delete", passive_deletes=True)

    tags = association_proxy("_tags", "name")

    # Column property
    like_count = None


# Column properties
follow_alias = follow.alias()
# The follow alias is necessary because the followers+following relationship will join on follow, so we need another
# name to refer to follow in this subquery.

User.post_count = column_property(select([func.count()]).where(Post.id == User.id), deferred=True)
User.follower_count = column_property(select([func.count()]).where(follow_alias.c.to_user_id == User.id), deferred=True)
User.following_count = column_property(select([func.count()]).where(follow_alias.c.from_user_id == User.id),
                                       deferred=True)
Post.like_count = column_property(select([func.count()]).where(Post.id == post_like.c.post_id))
