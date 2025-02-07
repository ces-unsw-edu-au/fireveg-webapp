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
from webapp.models.AdminUsersJwtTokens import AdminUsersJwtTokens
from functools import wraps
from webapp.middlewares.adminAuthMiddleware import token_required
from webapp.helpers.jwtTokenHelpers import generate_token
import os
from dotenv import load_dotenv
load_dotenv()
# bp = Blueprint('sites', __name__, url_prefix='/sites')
# bp = Blueprint('sites', __name__, url_prefix='/sites')
admin_user_routes = Blueprint('admin_user_routes', __name__)



@admin_user_routes.route('/users', methods=['GET'])
@token_required
def get_users(objAdminUser):
    objAllAdminUsers = AdminUsers.query.all()
    
    # Create a list of user dictionaries
    objAdminUsers = [{'id': user.id, 'username': user.username, 'email': user.email, 'name': user.name} for user in objAllAdminUsers]
    
    # Get the total count of users
    total_admin_users = AdminUsers.query.count()
    print("total_admin_users")
    print("total_admin_users")
    print("total_admin_users")
    print(total_admin_users)
    # Create the response dictionary
    response = {
        'error': False, 'msg': 'Admin Users retrieved successfully',
        'objAdminUsers': objAdminUsers, 'total_admin_users': total_admin_users
    }
    
    # Return the response as JSON
    return jsonify(response)

@admin_user_routes.route('/users', methods=['POST'])
@token_required
def create_user(objAdminUser):
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



@admin_user_routes.route('/users/<user_id>', methods=['GET'])
@token_required
def get_user(objAdminUser, user_id):
    try:
        objAdminUser = AdminUsers.query.get(user_id)
        if objAdminUser:
            user_data = {
                'id': objAdminUser.id,
                'username': objAdminUser.username,
                'email': objAdminUser.email,
                'name': objAdminUser.name,
                # Add other properties as needed
            }
            return jsonify({"error": False,'objAdminUser': user_data})
        else:
            return jsonify({"error": True,'msg': 'User not found'}), 404
    except Exception as e:
        print(e)
        print(f'Error getting user: {str(e)}')
        # return jsonify({"error": True, 'msg': f'Error: {str(e)}'}), 500
        return jsonify({"error": True,'msg': f'Ops something went wrong, please try again.'}), 500


@admin_user_routes.route('/users/<user_id>', methods=['PUT'])
@token_required
def update_user(objAdminUser, user_id):
    try:
        objAdminUser = AdminUsers.query.get(user_id)
        if objAdminUser:
            data = request.get_json()
            objAdminUser.username = data['email']
            objAdminUser.email = data['email']
            objAdminUser.name = data['name']
            db.session.commit()
            return jsonify({"error": False,'msg': 'Admin User updated successfully'})
        else:
            return jsonify({"error": True,'msg': 'Admin User not found'}), 404
    except Exception as e:
        print(e)
        print(f'Error updating Admin User: {str(e)}')
        return jsonify({"error": True, 'msg': f'Error updating Admin User, Please try again.'}), 500
        # return jsonify({"error": True,'message': f'Error: '}), 500


@admin_user_routes.route('/users/<user_id>', methods=['DELETE'])
@token_required
def delete_user(objAdminUser, user_id):
    objAdminUser = AdminUsers.query.get(user_id)
    if objAdminUser:
        AdminUsersJwtTokens.query.filter_by(user_id=user_id).delete()
        db.session.delete(objAdminUser)
        db.session.commit()
        return jsonify({"error": False, 'msg': 'Admin User deleted successfully'})
    else:
        return jsonify({"error": True, 'msg': 'User not found'}), 404


@admin_user_routes.route('/login', methods=['POST'])
def login():
    response = {}
    status_code = 200  # Default status code
    try:
        data = request.get_json()
        objAdminUser = AdminUsers.query.filter_by(email=data['email']).first()
        print('objAdminUser')
        print(objAdminUser)
        print('objAdminUser.id')
        print(objAdminUser.id)
        if objAdminUser and check_password_hash(objAdminUser.password, data['password']):
            token = generate_token(objAdminUser.id)
            expires_at = datetime.utcnow() + timedelta(days=50)
            newUserJWTToken = AdminUsersJwtTokens(
                user_id=objAdminUser.id, token=token, 
                expires_at=expires_at
            )
            db.session.add(newUserJWTToken)
            db.session.commit()
            response = {"error": False, 'msg': 'success.', "token": token}
            status_code = 200  # Bad Request
        else:
            response = {"error": True, 'msg': 'Invalid credentials'}
            status_code = 401
        # return jsonify({"error": False, 'msg': 'Admin User created successfully'}), 201
    except Exception as e:
        # db.session.rollback()  # Rollback the transaction in case of an error
        print(e)
        print(f'Error login User: {str(e)}')
        response = {"error": True, 'msg': f'Error login User, Please try again.'}
        status_code = 500

    return jsonify(response), status_code



@admin_user_routes.route('/auth', methods=['GET'])
@token_required
def auth(objAdminUser):
    try:
        # print('objAdminUser')
        # print(objAdminUser)
        # print('objAdminUser.id')
        # print(objAdminUser.id)
        # objAdminUserData = AdminUsers.query.get(objAdminUser.id)
        # print('objAdminUserData in auth')
        # print('objAdminUserData in auth')
        # print('objAdminUserData in auth')
        # print(objAdminUserData)
        # print('objAdminUserData.id')
        # print(objAdminUserData.id)
        # print('objAdminUserData.username')
        # print(objAdminUserData.username)
        # print('objAdminUserData.email')
        # print(objAdminUserData.email)
        # print('objAdminUserData.name')
        # print(objAdminUserData.name)
        if objAdminUser:
            # user_data = {
            #     "isAuth": True,
            #     'id': objAdminUser.id,
            #     'username': objAdminUser.username,
            #     'email': objAdminUser.email,
            #     'name': objAdminUser.name,
            #     # Add other properties as needed
            # }
            return jsonify({
                "error": False,
                "isAuth": True,
                'id': objAdminUser.id,
                'username': objAdminUser.username,
                'email': objAdminUser.email,
                'name': objAdminUser.name,
            })
        
        else:
            return jsonify({"error": True,"isAuth": False,'msg': 'User not found'}), 404
    except Exception as e:
        print(e)
        print(f'Error getting user: {str(e)}')
        # return jsonify({"error": True, 'msg': f'Error: {str(e)}'}), 500
        return jsonify({"error": True,"isAuth": False,'msg': f'Ops something went wrong, please try again.'}), 500

@admin_user_routes.route('/logout', methods=['POST'])
@token_required
def logout(objAdminUser):
    try:
        token = request.headers['authorization']
        objAdminUserJwtToken = AdminUsersJwtTokens.query.filter_by(user_id=objAdminUser.id,token=token).first()
        if objAdminUserJwtToken:
            db.session.delete(objAdminUserJwtToken)
            db.session.commit()
            return jsonify({"error": False, 'msg': 'Admin User logged out successfully'})
        else:
            return jsonify({"error": True, 'msg': 'User not found'}), 404
        
    except Exception as e:
        print(e)
        print(f'Error getting user: {str(e)}')
        # return jsonify({"error": True, 'msg': f'Error: {str(e)}'}), 500
        return jsonify({"error": True,'msg': f'Ops something went wrong, please try again.'}), 500
