from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db
from webapp.pg import get_pg_connection
from datetime import datetime, timedelta

bp = Blueprint('sites', __name__, url_prefix='/sites')

@bp.route('/list')
def sites_list():
    pg = get_pg_connection()
    cur = pg.cursor()
    cur.execute('SELECT site_label, location_description, elevation, ST_X(ST_Transform(geom,4326)) , ST_Y(ST_Transform(geom,4326)) FROM form.field_site ORDER BY site_label;')
    site_list = cur.fetchall()
    cur.close()
    return render_template('sites/list.html', pairs=site_list, the_title="Field Work locations")

@bp.route('/info/<id>')
def site_info(id):
    qry1 = "SELECT site_label,location_description,elevation,st_x(geom),st_y(geom),st_srid(geom) FROM form.field_site WHERE site_label='%s';"
    qry2 = "SELECT visit_date,visit_description,userkey,givennames,surname,otherobserver,survey_name FROM form.field_visit LEFT JOIN form.observerid ON mainobserver=userkey WHERE visit_id='%s' ORDER BY visit_date ASC;"
    qry3 = "SELECT fire_name, fire_date, fire_date_uncertain, how_inferred, cause_of_ignition FROM form.fire_history WHERE visit_id='%s' ORDER BY fire_date ASC"
    pg = get_pg_connection()
    cur = pg.cursor()
    cur.execute(qry1 % id)
    try:
        site_res = cur.fetchone()
    except:
        return f"<h1>Invalid site label: {id}</h1>"
    cur.execute(qry2 % (id))
    try:
        visit_res = cur.fetchall()
    except:
        return f"<h1>Invalid site label: {id}</h1>"
    cur.execute(qry3 % (id))
    try:
        fire_res = cur.fetchall()
    except:
        return f"<h1>Invalid site label: {id}</h1>"
    cur.close()
    return render_template('sites/info.html', info=site_res, visit=visit_res , fire=fire_res, the_title=id)

@bp.route('/visit/<id>/<dt>')
def visit_info(id,dt):
    return render_template('sites/visit.html', site=id,visit=dt)
