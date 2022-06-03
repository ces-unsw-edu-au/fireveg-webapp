import os
import logging
from flask import Flask, render_template


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'webapp.sqlite'),
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

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # we can write an 'about' page
    @app.route('/about')
    def about():
        return render_template('about.html', the_title="Home / About")
    @app.route('/documentation')
    def documentation():
        return render_template('documentation.html', the_title="Home / Documentation")
    @app.route('/index')
    def index():
        return render_template('home.html', the_title="Home ")
    @app.route('/summary')
    def summary():
        return render_template('index.html', the_title="Home / Summary ")

    from . import db
    db.init_app(app)
    from . import pg
    pg.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    #from . import blog
    #app.register_blueprint(blog.bp)

    app.add_url_rule('/', endpoint='index')

    from . import sites
    app.register_blueprint(sites.bp)
    from . import visits
    app.register_blueprint(visits.bp)
    from . import species
    app.register_blueprint(species.bp)
    from . import traits
    app.register_blueprint(traits.bp)
    from . import biblio
    app.register_blueprint(biblio.bp)
    from . import dataentry
    app.register_blueprint(dataentry.bp)
    from . import dataxport
    app.register_blueprint(dataxport.bp)

    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers

    return app
