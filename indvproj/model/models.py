__author__ = 'Chrille'
from sqlalchemy.dialects import postgresql
#from sqlalchemy import db.Column, db.Integer, db.String, db.DateTime, db.ForeignKey, PrimaryKeyConstraint
#from model.database import db
from indvproj import db
import datetime

collection_has_post = db.Table('collection_has_post',
                               db.Column('cid', db.Integer, db.ForeignKey('collection.collectionid'), primary_key=True),
                               db.Column('pid', db.Integer, db.ForeignKey('post.postid'), primary_key=True)
)
collection_has_link = db.Table('collection_has_link',
                               db.Column('cid', db.Integer, db.ForeignKey('collection.collectionid'), primary_key=True),
                               db.Column('linkid', db.Integer, db.ForeignKey('link.linkid'), primary_key=True)
)
category_has_moderator = db.Table('category_has_moderator',
                                  db.Column('categoryid', db.Integer, db.ForeignKey('category.categoryid'),
                                            primary_key=True),
                                  db.Column('userid', db.Integer, db.ForeignKey('user.userid'), primary_key=True)
)


class User(db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(postgresql.BYTEA, nullable=False)
    salt = db.Column(postgresql.BYTEA, nullable=False)
    postscreated = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    allcomments = db.relationship('Comment', backref='user', lazy='dynamic')
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    status = db.Column(db.Integer, db.ForeignKey('status.statusid'), default=1, nullable=True)
    statusobject = db.relationship('Status', lazy='joined')
    posts = db.relationship('Post', backref='user', lazy='dynamic')
    collections = db.relationship('Collection', backref='user', lazy='dynamic')
    moderator = db.relationship('Category', secondary=category_has_moderator,
                                backref=db.backref('moderators', lazy='dynamic'))

    def __init__(self, username, email, password, salt):
        self.username = username
        self.email = email
        self.password = password
        self.postscreated = 0
        self.comments = 0
        self.salt = salt

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.userid

    def __unicode__(self):
        return self.username


class Status(db.Model):
    statusid = db.Column(db.Integer, primary_key=True, nullable=False)
    statusname = db.Column(db.String(25), nullable=False, unique=True)

    def __init__(self, statusname):
        self.statusname = statusname

    def __repr__(self):
        return '<Status {}>'.format(self.statusname)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'))
    postid = db.Column(db.Integer, db.ForeignKey('post.postid'))
    commentid = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    content = db.Column(db.String(2000))
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, userid, postid, content, commentid=None):
        self.userid = userid
        self.postid = postid
        self.content = content
        self.commentid = commentid

    def __repr__(self):
        return '<Comment {}>'.format(self.content[:15])


class UserGroup(db.Model):
    ugid = db.Column(db.Integer, primary_key=True)
    ugname = db.Column(db.String(50), unique=True)

    def __init__(self, ugname):
        self.ugname = ugname

    def __repr__(self):
        return '<User_Group {}>'.format(self.ugname)


ug_has_v = db.Table('ug_has_v',
                    db.Column('ugid', db.Integer, db.ForeignKey('user_group.ugid'), primary_key=True),
                    db.Column('vid', db.Integer, db.ForeignKey('visibility.vid'), primary_key=True)
)


class Category(db.Model):
    categoryid = db.Column(db.Integer, primary_key=True)
    categoryname = db.Column(db.String(100), unique=True, nullable=False)
    categorytitle = db.Column(db.String(100))
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    posts = db.relationship('Post', backref='category', lazy='dynamic')

    def __init__(self, categoryname, title="Default title"):
        self.categoryname = categoryname
        self.categorytitle = title

    def __repr__(self):
        return '<Category {}>'.format(self.categoryname)


# TODO: Change from post to using only links. Makes more sense this way
# Or does it? Hard to say really. Gotta think really hard about it. But it doesn't matter that much since I can just
# Change it later if I need too
class Collection(db.Model):
    collectionid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    title = db.Column(db.String(250), nullable=False)

    def __init__(self, userid, title):
        self.userid = userid
        self.title = title

    def __repr__(self):
        return '<Collection {} created by {}, collectionid: {}>'.format(self.title, self.user.username,
                                                                        self.collectionid)


class Post(db.Model):
    postid = db.Column(db.Integer, primary_key=True)
    createdby = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    timeposted = db.Column(db.DateTime, nullable=False)
    views = db.Column(db.Integer, default=0)
    content = db.Column(db.String(2000), nullable=False)
    typeid = db.Column(db.Integer, db.ForeignKey('type.typeid'), nullable=True)
    title = db.Column(db.String(250), nullable=False)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    collections = db.relationship('Collection', secondary=collection_has_post,
                                  backref=db.backref('posts', lazy='dynamic'))
    categoryid = db.Column(db.Integer, db.ForeignKey('category.categoryid'), nullable=False)

    def __init__(self, createdby, timeposted, content, typeid, title, categoryid):
        self.createdby = createdby
        self.timeposted = timeposted
        self.content = content
        self.typeid = typeid
        self.title = title
        self.views = 0
        self.typeid = typeid
        self.categoryid = categoryid

    def __repr__(self):
        return '<Post {}>'.format(self.title)


class Link(db.Model):
    linkid = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(350))

    collection = db.relationship('Collection', secondary=collection_has_link,
                                 backref=db.backref('links', lazy='dynamic'))

    def __init__(self, link):
        self.link = link

    def __repr__(self):
        return '<Link {}>'.format(self.link)


class Type(db.Model):
    typeid = db.Column(db.Integer, primary_key=True)
    typename = db.Column(db.String(50), unique=True)

    def __init__(self, typename):
        self.typename = typename

    def __repr__(self):
        return '<Type {}>'.format(self.typename)


class Visibility(db.Model):
    vid = db.Column(db.Integer, primary_key=True)
    vname = db.Column(db.String(50), unique=True)

    def __init__(self, vname):
        self.vname = vname

    def __repr__(self):
        return '<Visibility {}>'.format(self.vname)


var = """
class UG_has_V(db.Model):
    __tablename__ = 'ughasv'
    ugid = db.Column(db.Integer, db.ForeignKey('usergroup.ugid'))
    vid = db.Column(db.Integer, db.ForeignKey('visibility.vid'))

    __table_args__ = (
        ('ugid', 'vid'),
        {},
    )

    def __init__(self, ugid, vid):
        self.ugid = ugid
        self.vid = vid

    def __repr__(self):
        return '<UG_has_V {} {}>'.format(self.ugid, self.vid)
ug_has_v = db.Table('ug_has_v',
                    db.Column('ugid',db.Integer,db.ForeignKey('usergroup.ugid')),
                    db.Column('vid', db.Integer,db.ForeignKey('visibility.vid'))
)

collection_has_post = db.Table('collection_has_post',
                               db.Column('cid',db.Integer, db.ForeignKey('collection.groupid')),
                               db.Column('pid',db.Integer, db.ForeignKey('post.postid'))
)
"""
