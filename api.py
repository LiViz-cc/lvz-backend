import os

from dotenv import load_dotenv
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api

from database import initialize_db
from resources import initialize_routes

# load environment variables from .env
load_dotenv()

# create flask app
app = Flask(__name__)
# set app config
app.config['MONGODB_SETTINGS'] = {
    'host': os.getenv('MONGODB_HOST')
}
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# enable cors
cors = CORS(app)

# create restful api on top of the app
api = Api(app)

# initialize encrypt
bcrypt = Bcrypt(app)

# initialize jwt manager
jwt = JWTManager(app)

# initialize MongoDB connection
initialize_db(app)

# initialize resources routers
initialize_routes(api)


if __name__ == '__main__':
    # load start config
    env = os.getenv('ENV')
    port = int(os.getenv('PORT'))

    # start server
    if env == 'development':
        app.run(debug=True, port=port)
    elif env == 'production':
        from waitress import serve
        serve(app, host="0.0.0.0", port=port)
    else:
        raise RuntimeError('Fail to start server with ENV=%s!' % env)
