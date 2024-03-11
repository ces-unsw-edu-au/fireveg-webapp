import os
import logging
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()
# import sendgrid
# from sendgrid.helpers.mail import *
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # app.config.from_mapping(
    #     SECRET_KEY='dev',
    #     # for authentication
    #     # DATABASE=os.path.join(app.instance_path, 'webapp.sqlite'),
    #     # path to files for data entry and export
    #     UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploaded_files'),
    #     #MAX_CONTENT-PATH=
    #     DATAENTRY=os.path.join(app.instance_path, 'data-entry.xlsx'),
    #     PROFORMA=os.path.join(app.instance_path, 'field-work-proforma.docx'),
    #     DATAXPORT=os.path.join(app.instance_path, 'data-summary-export.xlsx'),
    #     RECORDXPORT=os.path.join(app.instance_path, 'data-all-records-export.xlsx'),
    # )
    app.config['SECRET_KEY'] = 'dev'

    # Comment out or remove the SQLite-specific configuration
    # app.config['DATABASE'] = os.path.join(app.instance_path, 'webapp.sqlite')

    app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, 'uploaded_files')
    app.config['DATAENTRY'] = os.path.join(app.instance_path, 'data-entry.xlsx')
    app.config['PROFORMA'] = os.path.join(app.instance_path, 'field-work-proforma.docx')
    app.config['DATAXPORT'] = os.path.join(app.instance_path, 'data-summary-export.xlsx')
    app.config['RECORDXPORT'] = os.path.join(app.instance_path, 'data-all-records-export.xlsx')

    # Set the PostgreSQL database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # db = SQLAlchemy(app)
    # print(os.getenv('DATABASE_URI'))
    # print(os.getenv('DATABASE_URI'))
    # print(os.getenv('DATABASE_URI'))
    # print(os.getenv('DATABASE_URI'))
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
    
     # Enable CORS for API routes and specify allowed origins
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://fireecologyplants.net", "https://fireecologyplants.net"]}})
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
    from webapp.db import db
    # print(db)
    db.init_app(app)
    # print("after")
    # print(db)
    from webapp.models import Users, Posts, AdminUsers, RoleUpgradeRequests, UserJwtTokens, AdminUsersJwtTokens
    migrate = Migrate(app, db)
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

    from webapp.api.admin_user_routes import admin_user_routes 
    from webapp.api.admin_webapp_user_routes import admin_webapp_user_routes 
    from webapp.api.admin.upgrade_roles.admin_role_upgrade_requests_routes import admin_role_upgrade_requests_routes  

    app.register_blueprint(admin_user_routes, url_prefix='/api/admin-users')

    app.register_blueprint(admin_webapp_user_routes, url_prefix='/api/admin-webapp-users')

    app.register_blueprint(admin_role_upgrade_requests_routes, url_prefix='/api/admin-role-upgrade-requests')

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

    # print(os.environ.get('SENDGRID_API_KEY'))
    # print(os.environ.get('SENDGRID_API_KEY'))
    # print(os.environ.get('SENDGRID_API_KEY'))
    # message = Mail(
    # # from_email='j.ferrer@unsw.edu.au',fireecologyplants.net
    # from_email='j.ferrer@fireecologyplants.net',
    # to_emails='usamamashkoor@gmail.com',
    # subject='This is test email',
    # html_content='<strong>Hi Usama</strong>')
    # try:
    #     sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    #     response = sg.send(message)
    #     print("response")
    #     print("response")
    #     print(response)
    #     print("response.status_code")
    #     print("response.status_code")
    #     print(response.status_code)
    #     print("response.body")
    #     print("response.body")
    #     print(response.body)
    #     print("response.headers")
    #     print("response.headers")
    #     print(response.headers)
    # except Exception as e:
        # print("e")
        # print("e")
        # print(e)
        # print("e.message")
        # print("e.message")
        # print(e.message)
    # sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    # from_email = Email("j.ferrer@unsw.edu.au")
    # to_email = To("usamamashkoor@gmail.com")
    # subject = "Sending with SendGrid is Fun"
    # content = Content("text/plain", "Hi Usama")
    # mail = Mail(from_email, to_email, subject, content)
    # response = sg.client.mail.send.post(request_body=mail.get())
    # print('response')
    # print(response)
    # print('response.status_code')
    # print(response.status_code)
    # print('response.body')
    # print(response.body)
    # print('response.headers')
    # print(response.headers)
    # Added this for handling error messages
    # this is only relevant when using gunicorn
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers

    
    # This is it!
    return app
