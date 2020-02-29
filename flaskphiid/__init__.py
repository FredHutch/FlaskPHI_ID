# flaskphiid.py or flaskphiid/__init__.py
import logging
import os
from flask import Flask, render_template

formatter = logging.Formatter(
    "%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")

logger = logging.getLogger()
streamhandler = logging.StreamHandler()
streamhandler.setLevel(logging.INFO)
streamhandler.setFormatter(formatter)
logger.addHandler(streamhandler)
logger.setLevel(logging.INFO)


# load medlp interface
from compmed.CompMedServiceInterface import CompMedServiceInterface
from compmed_utils import json_parser_util as JSONParser
compmedInterface = CompMedServiceInterface(JSONParser.xform_dict_to_json)
#load HutchNER interface
from HutchNERPredict import hutchner as hutchnerpredict
hutchNERInterface = hutchnerpredict.HutchNER()

def index():
    return render_template(
        'index.html', name="User")


def create_app(test_config=None):
    # create and configure the flaskphiid
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.urandom(24),
        DATABASE=os.path.join(app.instance_path, 'flaskphiid.sqlite'),
    )
    app.url_map.strict_slashes = False

    if test_config is None:
        # Now we can access the configuration variables via flaskphiid.config["VAR_NAME"].
        # Load the default configuration
        #app.config.from_object('config.default')

        # Load the configuration from the instance folder
        '''
        TODO: the is an unexpected interaction between venv, setup.py install, and where instance folders get located in venv
        until this is figured out, the app will rely on a environment var to find the config 
        '''
        #app.config.from_pyfile('config.py')

        # Load the file specified by the APP_CONFIG_FILE environment variable
        # Variables defined here will override those in the default configuration
        app.config.from_envvar('APP_CONFIG_FILE', silent=True)

    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    #set up database
    #from . import db
    #db.init_app(app)

    hutchNERInterface.load_model(input_path=app.config['HUTCHNER_MODEL'])
    hutchNERInterface.load_clusters(input_path=app.config['CLINIC_NOTE_CLUSTERS'])

    from flaskphiid import compmedner, hutchner, identifyphi
    app.register_blueprint(compmedner.bp)
    app.register_blueprint(hutchner.bp)
    app.register_blueprint(identifyphi.bp)

    # make url_for('index') == url_for('blog.index')
    # in another flaskphiid, you might define a separate main index here with
    # flaskphiid.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    app.add_url_rule('/', view_func=index)

    return app


