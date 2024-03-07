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
    # objAllUsers = Users.query.all()
    page = request.args.get('page', 1, type=int)
    users_per_page = request.args.get('perPage', 10, type=int)
    users = Users.query.paginate(page=page, per_page=users_per_page, error_out=False)
    objAllUsers = users.items
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
        'objWebAppUsers': objWebAppUsers, 'total_users': total_users, 
        'page': page,
        'pageCount': users.pages 
    }
    
    # Return the response as JSON
    return jsonify(response)

@admin_webapp_user_routes.route('/users/<user_id>', methods=['GET'])
@token_required
def get_user(objAdminUser, user_id):
    try:
        objUser = Users.query.get(user_id)
        if objUser:
            user_data = {
                'id': objUser.id,
                'role': objUser.role.value,
                'email': objUser.email,
            }
            return jsonify({"error": False,'objWebAppUser': user_data})
        else:
            return jsonify({"error": True,'msg': 'User not found'}), 404
    except Exception as e:
        print(e)
        print(f'Error getting user: {str(e)}')
        # return jsonify({"error": True, 'msg': f'Error: {str(e)}'}), 500
        return jsonify({"error": True,'msg': f'Ops something went wrong, please try again.'}), 500


@admin_webapp_user_routes.route('/users/<user_id>', methods=['PUT'])
@token_required
def update_user(objAdminUser, user_id):
    try:
        objUser = Users.query.get(user_id)
        if objUser:
            data = request.get_json()
            objUser.username = data['email']
            objUser.email = data['email']
            objUser.role = data['role']
            db.session.commit()
            return jsonify({"error": False,'msg': 'Web App User updated successfully'})
        else:
            return jsonify({"error": True,'msg': 'Web App User not found'}), 404
    except Exception as e:
        print(e)
        print(f'Error updating Web App User: {str(e)}')
        return jsonify({"error": True, 'msg': f'Ops something went wrong, please try again.'}), 500
        # return jsonify({"error": True,'message': f'Error: {str(e)}'}), 500


# @admin_webapp_user_routes.route('/users/<user_id>', methods=['DELETE'])
# @token_required
# def delete_user(objAdminUser, user_id):
#     objUser = Users.query.get(user_id)
#     if objUser:
#         db.session.delete(objUser)
#         db.session.commit()
#         return jsonify({"error": False, 'msg': 'Web App User deleted successfully'})
#     else:
#         return jsonify({"error": True, 'msg': 'User not found'}), 404

