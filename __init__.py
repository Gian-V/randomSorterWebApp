import os
from randomSorterWebApp.blueprints import index
from flask import Flask, session

bps = [index.bp]

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)

    app.config['DATABASE'] = os.path.join(app.instance_path, '../instance/db.sqlite')
    app.config['UPLOAD_FOLDER'] = "./randomSorterWebApp/lists/"
    app.config['MAX_CONTENT_PATH'] = 1048576
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    for bp in bps:
        app.register_blueprint(bp)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
