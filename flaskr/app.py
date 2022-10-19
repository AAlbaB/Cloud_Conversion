from flaskr import create_app
from flask_restful import Api
from flask_jwt_extended import JWTManager

from .modelos import db, User, File
from .modelos import FileSchema, UserSchema
from .vistas import VistaUser, VistaUsers, VistaSignIn, VistaLogIn, \
                    VistaFilesUser

app = create_app('default')
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

api = Api(app)
api.add_resource(VistaUsers, '/users')
api.add_resource(VistaUser, '/users/<int:id_user>')
api.add_resource(VistaSignIn, '/auth/signup')
api.add_resource(VistaLogIn, '/auth/login')
api.add_resource(VistaFilesUser, '/tasks/<int:id_user>')

jwt = JWTManager(app)