# flaskdeid.py or flaskdeid/__init__.py
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
from amazonserviceinterface.MedLPServiceInterface import MedLPServiceInterface
import clinicalnotesprocessor.JSONParser as JSONParser
medlpInterface = MedLPServiceInterface(JSONParser.xform_dict_to_json)
#load HutchNER interaface
from HutchNERPredict import hutchner as hutchnerpredict
hutchNERInterface = hutchnerpredict.HutchNER()

def index():
    return render_template(
        'index.html', name="User")


def create_app(test_config=None):
    # create and configure the flaskdeid
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.urandom(24),
        DATABASE=os.path.join(app.instance_path, 'flaskdeid.sqlite'),
    )

    if test_config is None:
        # Now we can access the configuration variables via flaskdeid.config["VAR_NAME"].
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
    from . import db
    db.init_app(app)

    hutchNERInterface.load_model(input_path=app.config['HUTCHNER_MODEL'])

    from flaskdeid import medlp, preprocessing, sectionerex, hutchner, deid
    app.register_blueprint(medlp.bp)
    app.register_blueprint(preprocessing.bp)
    app.register_blueprint(sectionerex.bp)
    app.register_blueprint(hutchner.bp)
    app.register_blueprint(deid.bp)

    # make url_for('index') == url_for('blog.index')
    # in another flaskdeid, you might define a separate main index here with
    # flaskdeid.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    app.add_url_rule('/', view_func=index)

    return app


