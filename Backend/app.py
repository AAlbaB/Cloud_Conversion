from api import create_app
from flask_cors import CORS
from flask_restful import Api
from flask_jwt_extended import JWTManager

from api.modelos import db
from api.vistas import VistaUser, VistaUsers, VistaSignIn, VistaLogIn, \
                        VistaTask, VistaTasksUser, VistaFiles

app = create_app()
app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()
cors = CORS(app)

api = Api(app)
api.add_resource(VistaUsers, '/users')
api.add_resource(VistaUser, '/users/<int:id_user>')
api.add_resource(VistaSignIn, '/auth/signup')
api.add_resource(VistaLogIn, '/auth/login')
api.add_resource(VistaTasksUser, '/api/tasks')
api.add_resource(VistaTask, '/api/tasks/<int:id_task>')
api.add_resource(VistaFiles, '/api/files/<string:fileName>')

jwt = JWTManager(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0')