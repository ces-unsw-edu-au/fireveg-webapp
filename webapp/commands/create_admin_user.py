# create_admin_script.py
import os
from dotenv import load_dotenv
load_dotenv()
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from webapp import create_app  # Import the create_app function from your Flask app module
from webapp.models.AdminUsers import AdminUsers  # Import the Admin User model from your Flask app
from webapp.db import db
import click
# Replace 'your_flask_app' with the actual name of your Flask app module

# Configure the PostgreSQL database connection
# DATABASE_URL = os.getenv('DATABASE_URI')
# engine = create_engine(DATABASE_URL)

# # Bind the engine to the SQLAlchemy session
# Session = sessionmaker(bind=engine)
# session = Session()
@click.command('create_admin_user')
@click.option('--email', prompt='Admin Email', help='Admin user email')
@click.option('--password', prompt='Admin Password', hide_input=True, confirmation_prompt=True, help='Admin user password')
def create_admin_user(email, password):
    """
    Create an admin user.
    """
    # Check if the admin user already exists
    # email = 'adminjferrer@fireecologyplants.net'
    # password = "adminjferrer_12345678"
    existing_admin = AdminUsers.query.filter_by(email=email).first()
    # print("existing_admin")
    print("existing_admin")
    print(existing_admin)
    if existing_admin:
        print('Test admin user already exists!')
        return

    # Create the admin user
    admin_user = AdminUsers(
        name=email, username=email, 
        email=email, password=generate_password_hash(password)
    )
    db.session.add(admin_user)
    db.session.commit()
    # print("admin_user")
    # print("admin_user")
    # print(admin_user)
    # click.echo('Test admin user created successfully in the database.')
    # click.echo('Test admin user created successfully in the database.')
    click.echo('Test admin user created successfully in the database.')
    print('Test admin user created successfully!')
