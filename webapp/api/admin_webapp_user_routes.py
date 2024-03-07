from flask import (
    Blueprint, flash, g, redirect, render_template, jsonify, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash
from webapp.auth import login_required
from webapp.db import get_db, db
from webapp.pg import get_pg_connection
from datetime import datetime, timedelta
import folium
import jwt
from folium.plugins import MarkerCluster
from webapp.models.AdminUsers import AdminUsers
from webapp.models.Users import Users
from webapp.models.AdminUsersJwtTokens import AdminUsersJwtTokens
from functools import wraps
from webapp.middlewares.adminAuthMiddleware import token_required
from webapp.helpers.jwtTokenHelpers import generate_token
import os
from dotenv import load_dotenv
load_dotenv()
# bp = Blueprint('sites', __name__, url_prefix='/sites')
# bp = Blueprint('sites', __name__, url_prefix='/sites')
admin_webapp_user_routes = Blueprint('admin_webapp_user_routes', __name__)


@admin_webapp_user_routes.route('/users', methods=['GET'])
@token_required
def get_users(objAdminUser):
    objAllUsers = Users.query.all()
    
    # Create a list of user dictionaries
    objWebAppUsers = [
        {'id': user.id, 'username': user.username, 'email': user.email, 'role': user.role.value} for user in objAllUsers
    ]
    
    # Get the total count of users
    total_users = Users.query.count()
    print("total_users")
    print("total_users")
    print("total_users")
    print(total_users)
    # Create the response dictionary
    response = {
        'error': False, 'msg': 'Users retrieved successfully.',
        'objWebAppUsers': objWebAppUsers, 'total_users': total_users
    }
    
    # Return the response as JSON
    return jsonify(response)

