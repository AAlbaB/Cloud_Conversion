from marshmallow_sqlalchemy import SQLAlchemySchema
from marshmallow import fields, Schema
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
  
class File(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    timeStamp = db.Column(db.DateTime, default = datetime.now)
    fileName = db.Column(db.String(256))
    newFormat = db.Column(db.String(20))
    status = db.Column(db.String(10), default = 'uploaded')
    user = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(128))
    email = db.Column(db.String(128))
    files = db.relationship('File', cascade='all, delete, delete-orphan')

class UserSchema(SQLAlchemySchema):
    class Meta:
        model = User
        include_relationships = True
        include_fk = True
        load_instance = True

    id = fields.Integer()
    username = fields.String()
    email = fields.String()

class FileSchema(SQLAlchemySchema):
    class Meta:
        model = File
        include_relationships = True
        include_fk = True
        load_instance = True

    id = fields.Integer()
    timeStamp = fields.String()
    fileName = fields.String()
    newFormat = fields.String()
    status = fields.String()
    user = fields.Integer()

    