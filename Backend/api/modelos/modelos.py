from marshmallow_sqlalchemy import SQLAlchemySchema
from marshmallow import fields, Schema
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()
  
class File(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    timeStamp = db.Column(db.String(256), nullable = False)
    fileName = db.Column(db.String(256), nullable = False)
    newFormat = db.Column(db.String(3), nullable = False)
    status = db.Column(db.String(10), default = 'uploaded')
    pathOriginal = db.Column(db.String(1024), nullable = False)
    pathConvertido = db.Column(db.String(1024), nullable = False)
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

    