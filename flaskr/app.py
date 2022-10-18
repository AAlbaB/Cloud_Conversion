from flaskr import create_app
from flask_restful import Api
from flask_jwt_extended import JWTManager
from .modelos import db, User, File
from .modelos import FileSchema, UserSchema
from .vistas import VistaUser, VistaUsers, VistaSignIn, VistaLogIn

app = create_app('default')
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

api = Api(app)
api.add_resource(VistaUsers, '/users')
api.add_resource(VistaUser, '/user/<int:id_user>')
api.add_resource(VistaSignIn, '/signin')
api.add_resource(VistaLogIn, '/login')

jwt = JWTManager(app)

'''with app.app_context():
    user_schema = UserSchema()
    file_schema = FileSchema()
    us = User(username= 'Juanito', password='123456', email='correo de prueba')
    fil = File(fileName = 'Mi pista.mp3', newFormat = 'wav')
    us.files.append(fil)
    db.session.add(us)
    db.session.commit()
    print([user_schema.dumps(user) for user in User.query.all()])
    print([file_schema.dumps(file) for file in File.query.all()])'''
