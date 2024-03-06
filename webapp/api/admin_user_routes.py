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
from folium.plugins import MarkerCluster
from webapp.models.AdminUsers import AdminUsers
# bp = Blueprint('sites', __name__, url_prefix='/sites')
# bp = Blueprint('sites', __name__, url_prefix='/sites')
admin_user_routes = Blueprint('admin_user_routes', __name__)

@admin_user_routes.route('/users', methods=['GET'])
def get_users():
    objAllAdminUsers = AdminUsers.query.all()
    
    # Create a list of user dictionaries
    objAdminUsers = [{'id': user.id, 'username': user.username, 'email': user.email, 'name': user.name} for user in objAllAdminUsers]
    
    # Get the total count of users
    total_admin_users = AdminUsers.query.count()
    
    # Create the response dictionary
    response = {
        'error': False, 'msg': 'Admin Users retrieved successfully',
        'objAdminUsers': objAdminUsers, 'total_admin_users': total_admin_users
    }
    
    # Return the response as JSON
    return jsonify(response)

@admin_user_routes.route('/users', methods=['POST'])
def create_user():
    response = {}
    status_code = 200  # Default status code
    try:
        data = request.get_json()
        # Check for duplicate email
        existing_user = AdminUsers.query.filter_by(email=data['email']).first()
        print('existing_user')
        print(existing_user)
        if existing_user:
            # If a user with the same email exists
            response = {"error": True, 'msg': 'Email already exists. Please use a different email.'}
            status_code = 400  # Bad Request
        else:
            new_user = AdminUsers(
                name=data['name'], username=data['email'], 
                email=data['email'], password=generate_password_hash(data['password'])
            )
            db.session.add(new_user)
            db.session.commit()
            response = {"error": False, 'msg': 'Admin User created successfully'}
            status_code = 201
        # return jsonify({"error": False, 'msg': 'Admin User created successfully'}), 201
    except Exception as e:
        # db.session.rollback()  # Rollback the transaction in case of an error
        print(e)
        print(f'Error creating Admin User: {str(e)}')
        response = {"error": True, 'msg': f'Error creating Admin User, Please try again.'}
        status_code = 500

    return jsonify(response), status_code


@admin_user_routes.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    objAdminUser = AdminUsers.query.get(user_id)
    if objAdminUser:
        db.session.delete(objAdminUser)
        db.session.commit()
        return jsonify({"error": False, 'msg': 'Admin User deleted successfully'})
    else:
        return jsonify({"error": True, 'msg': 'User not found'}), 404