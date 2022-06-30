import os
import logging
from flask import Flask, render_template


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        # for authentication
        DATABASE=os.path.join(app.instance_path, 'webapp.sqlite'),
        # path to files for data entry and export
        DATAENTRY=os.path.join(app.instance_path, 'data-entry.xlsx'),
        DATAXPORT=os.path.join(app.instance_path, 'data-export.xlsx'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Here are some fixed routes:
    # we can write an 'about' page
    @app.route('/about')
    def about():
        return render_template('about.html', the_title="Home / About")
    # place for simple documentation of features for end user
    @app.route('/documentation')
    def documentation():
        return render_template('documentation.html', the_title="Home / Documentation")
    # this is the welcome page
    @app.route('/index')
    def index():
        return render_template('home.html', the_title="Home ")
    # this is the summary with links to the different modules
    @app.route('/summary')
    def summary():
        return render_template('index.html', the_title="Home / Summary ")

    #additional url rule for index
    app.add_url_rule('/', endpoint='index')

    # Initialise some app functions
    # databases: I use a sqlite solution for user registration and login: this is stored in the local instance folder
    from . import db
    db.init_app(app)
    # databases: content of the database is in a external postgresql database
    from . import pg
    pg.init_app(app)
    # I include here some functions for the export of xlsx files
    # do we need to call this here? probably not
    from . import xlinit
    xlinit.init_app(app)

    ## Blueprints

    # This is the authentication blueprint
    from . import auth
    app.register_blueprint(auth.bp)

    ## These are blueprints for each component or module

    # Field work data is handled by the sites and visits blueprints
    # This is the `Green table/module` from the original diagramm from DK
    from . import sites
    app.register_blueprint(sites.bp)
    from . import visits
    app.register_blueprint(visits.bp)

    ## All things related to the taxonomy should go to the species blueprint
    from . import species
    app.register_blueprint(species.bp)


    # this blueprint is for the fire ecology trait recorded from literature sources
    # This is the `Blue table/module` from the original diagramm from DK
    from . import traits
    app.register_blueprint(traits.bp)

    # this blueprint is for the list of references
    from . import biblio
    app.register_blueprint(biblio.bp)

    # These blueprints are for functions to import and export data in workbook format
    #
    from . import dataentry
    app.register_blueprint(dataentry.bp)
    from . import dataxport
    app.register_blueprint(dataxport.bp)

    # Added this for handling error messages
    # this is only relevant when using gunicorn
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers

    # This is it!
    return app
