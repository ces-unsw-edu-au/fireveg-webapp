from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db
from webapp.pg import get_pg_connection

bp = Blueprint('sites', __name__, url_prefix='/sites')

@bp.route('/list')
def sites_list():
    pg = get_pg_connection()
    cur = pg.cursor()
    cur.execute('SELECT site_label,location_description FROM form.field_site ORDER BY site_label;')
    site_list = cur.fetchall()
    cur.close()
    return render_template('sites/list.html', pairs=site_list, the_title="Field Work locations")

@bp.route('/info/<id>')
def site_info(id):
    pg = get_pg_connection()
    cur = pg.cursor()
    cur.execute("SELECT site_label,location_description,elevation,st_x(geom),st_y(geom),st_srid(geom) FROM form.field_site WHERE site_label='%s';" % id)
    try:
        site_qry = cur.fetchone()
    except:
        return f"<h1>Invalid site label: {id}</h1>"
    cur.close()
    return render_template('sites/info.html', info=site_qry, the_title=id)
