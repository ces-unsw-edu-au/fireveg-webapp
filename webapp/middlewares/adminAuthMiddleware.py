from flask import (
    Blueprint, flash, g, redirect, render_template, jsonify, request, url_for
)
from webapp.models.AdminUsersJwtTokens import AdminUsersJwtTokens
from webapp.models.AdminUsers import AdminUsers
from functools import wraps
import jwt
import os
from dotenv import load_dotenv
load_dotenv()
# decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        objAdminUser = None
        # print("request.headers")
        # print("request.headers")
        # print(request.headers)
        # jwt is passed in the request header
        if 'authorization' in request.headers:
            token = request.headers['authorization']
            # print("token")
            # print("token")
            # print(token)
        # return 200 if token is not passed
        if not token:
            return jsonify({
                'msg' : 'Token is missing !!',
                'isAuth': False,
                'error': True
            }), 200
  
        try:
            # print("token")
            # print("token")
            # print(token)
            # decoding the payload to fetch the stored details
            decoded_token = jwt.decode(token, os.getenv('JWT_SECRET_KEY'), algorithms=["HS256"])
            print("decoded_token in token_required")
            print("decoded_token in token_required")
            print(decoded_token)
            print("token in token_required")
            print("token in token_required")
            print(token)
            objAdminUserJwtToken = AdminUsersJwtTokens.query.filter_by(token = token).first()
            if objAdminUserJwtToken:
                user_id = decoded_token['sub']
                objAdminUser = AdminUsers.query.get(user_id)
                print('objAdminUser in token_required')
                print('objAdminUser in token_required')
                print(objAdminUser)
                if objAdminUser:
                    _msg = "admin user is valid"
                else:
                    return jsonify({
                        'msg' : 'invalid credentials 1!!',
                        'isAuth': False,
                        'error': True
                    }), 200
            else:
                return jsonify({
                    'msg' : 'invalid credentials 2!!',
                    'isAuth': False,
                    'error': True
                }), 200

        except:
            return jsonify({
                'msg' : 'invalid credentials 3!!',
                'isAuth': False,
                'error': True
            }), 200
        # returns the current logged in users context to the routes
        return  f(objAdminUser, *args, **kwargs)
  
    return decorated