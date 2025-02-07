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
from webapp.models.RoleUpgradeRequests import RoleUpgradeRequests
from webapp.models.AdminUsersJwtTokens import AdminUsersJwtTokens
from functools import wraps
from webapp.middlewares.adminAuthMiddleware import token_required
from webapp.helpers.jwtTokenHelpers import generate_token
import os
from dotenv import load_dotenv
from pprint import pprint
load_dotenv()
# bp = Blueprint('sites', __name__, url_prefix='/sites')
# bp = Blueprint('sites', __name__, url_prefix='/sites')
admin_role_upgrade_requests_routes = Blueprint('admin_role_upgrade_requests_routes', __name__)


@admin_role_upgrade_requests_routes.route('/upgrade-requests', methods=['GET'])
@token_required
def upgrade_requests(objAdminUser):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('perPage', 10, type=int)
    # objRoleUpgradeRequestsData = RoleUpgradeRequests.query.paginate(page=page, per_page=per_page, error_out=False)
    objRoleUpgradeRequestsData = RoleUpgradeRequests.query \
        .join(Users, RoleUpgradeRequests.user_id == Users.id) \
        .add_columns(Users.username, Users.email, Users.role, RoleUpgradeRequests.id, RoleUpgradeRequests.user_id, RoleUpgradeRequests.role_name, RoleUpgradeRequests.created_at) \
        .paginate(page=page, per_page=per_page, error_out=False)
    # objRoleUpgradeRequestsData = RoleUpgradeRequests.query \
    #     .join(Users, RoleUpgradeRequests.user_id == Users.id) \
    #     .paginate(page=page, per_page=per_page, error_out=False)
    print("objRoleUpgradeRequestsData")
    print("objRoleUpgradeRequestsData")
    pprint(objRoleUpgradeRequestsData)
    print("objRoleUpgradeRequestsData.items")
    print("objRoleUpgradeRequestsData.items")
    pprint(objRoleUpgradeRequestsData.items)
    objAllRoleUpgradeRequests = objRoleUpgradeRequestsData.items
    # Create a list of user dictionaries
    # objRoleUpgradeRequests = [
    #     {'id': user.id, 'role_name': user.role_name, 'user_id': user.user_id} for user in objAllRoleUpgradeRequests
    # ]
    # Create a list of role upgrade request dictionaries along with user data
    objRoleUpgradeRequests = []

    for role_upgrade_request in objAllRoleUpgradeRequests:
        print("role_upgrade_request")
        print("role_upgrade_request")
        pprint(role_upgrade_request)
        print("role_upgrade_request.created_at")
        print("role_upgrade_request.created_at")
        pprint(role_upgrade_request.created_at)
        # print("role_upgrade_request.users")
        # print("role_upgrade_request.users")
        # pprint(role_upgrade_request.users)
        entry = {
            'id': role_upgrade_request.id,
            'role_name': role_upgrade_request.role_name,
            'username': role_upgrade_request.username,
            'email': role_upgrade_request.email,
            'user_id': role_upgrade_request.user_id,
            'role': role_upgrade_request.role.value,
            'created_at': role_upgrade_request.created_at,
            # 'updated_at': role_upgrade_request.updated_at,
            # 'user_data': {
            #     'username': role_upgrade_request.user.username,
            #     'email': role_upgrade_request.user.email,
            #     'role': role_upgrade_request.user.role.value  # Assuming role is an enum
            # }
        }
        objRoleUpgradeRequests.append(entry)
    # Get the total count of users
    total_role_upgrade_requests = Users.query.count()
    print("total_role_upgrade_requests")
    print("total_role_upgrade_requests")
    print("total_role_upgrade_requests")
    print(total_role_upgrade_requests)
    # Create the response dictionary
    response = {
        # "objRoleUpgradeRequestsData": objRoleUpgradeRequestsData,
        'error': False, 'msg': 'Role Upgrade Requests retrieved successfully.',
        'objRoleUpgradeRequests': objRoleUpgradeRequests, 'total_role_upgrade_requests': total_role_upgrade_requests, 
        'page': page,
        'pageCount': objRoleUpgradeRequestsData.pages 
    }
    
    # Return the response as JSON
    return jsonify(response)

