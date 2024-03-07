from flask import (
    Blueprint, flash, g, redirect, render_template, jsonify, request, url_for
)
from datetime import datetime, timedelta
import folium
import jwt
from folium.plugins import MarkerCluster
from webapp.models.AdminUsers import AdminUsers
from webapp.models.AdminUsersJwtTokens import AdminUsersJwtTokens
from functools import wraps
from webapp.middlewares.adminAuthMiddleware import token_required
import os
from dotenv import load_dotenv
load_dotenv()

def generate_token(user_id):
    token_payload = {
        'exp': datetime.utcnow() + timedelta(days=50),
        'iat': datetime.utcnow(),
        'sub': str(user_id)
    }
    token = jwt.encode(token_payload, os.getenv('JWT_SECRET_KEY'), algorithm='HS256')
    return token