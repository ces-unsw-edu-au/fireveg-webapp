from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db
from webapp.pg import get_pg_connection
from datetime import datetime, timedelta
import folium
from folium.plugins import MarkerCluster

bp = Blueprint('visits', __name__, url_prefix='/visits')


@bp.route('/list', defaults={'survey': None})
@bp.route('/list/<survey>')
@login_required
def visits_list(survey):
    pg = get_pg_connection()
    cur = pg.cursor()
    if survey == None:
        qry='SELECT visit_id,visit_date,count(distinct sample_nr),count(distinct species_code) FROM form.field_visit v LEFT JOIN form.field_samples s USING(visit_id,visit_date) LEFT JOIN form.quadrat_samples q USING (visit_id,visit_date,sample_nr) GROUP BY visit_id,visit_date;'
    else:
        qry='SELECT visit_id,visit_date,count(distinct sample_nr),count(distinct species_code)  FROM form.field_visit v LEFT JOIN form.field_samples s USING(visit_id,visit_date) LEFT JOIN form.quadrat_samples q USING (visit_id,visit_date,sample_nr) WHERE survey_name=\'%s\' GROUP BY visit_id,visit_date;' % survey
    cur.execute(qry)
    visit_list = cur.fetchall()
    cur.close()
    return render_template('visits/list.html', visits=visit_list, survey=survey)

@bp.route('/<id>/<dt>')
@login_required
def visit_info(id,dt):
    qry1 = "SELECT site_label,location_description,elevation,st_x(geom),st_y(geom),st_srid(geom) FROM form.field_site WHERE site_label='%s';"
    qry2 = "SELECT visit_date,visit_description,userkey,givennames,surname,observerlist,survey_name FROM form.field_visit LEFT JOIN form.observerid ON mainobserver=userkey WHERE visit_id='%s' AND visit_date='%s' ORDER BY visit_date ASC;"

    qry3 = "SELECT measured_var,units,best,lower,upper FROM form.field_visit_vegetation_estimates WHERE visit_id='%s' AND visit_date='%s' ORDER BY measured_var ASC;"


    qry4 = "SELECT vegtype,vegcategoryid,confidenceid,threatenedecologicalcommunity FROM form.field_visit_vegetation WHERE visit_id='%s' AND visit_date='%s';"

    qry5 = "select sample_method,count(DISTINCT sample_nr) FROM form.field_samples WHERE visit_id='%s' AND visit_date='%s' GROUP BY sample_method;"

    qry6 = "SELECT DISTINCT family, species_code, species, \"scientificName\", \"speciesID\"::int, \"sortOrder\" FROM form.quadrat_samples LEFT JOIN species.caps ON \"speciesCode_Synonym\" = species_code::text WHERE visit_id='%s' AND visit_date='%s' ORDER BY \"sortOrder\";"

    pg = get_pg_connection()
    cur = pg.cursor()
    cur.execute(qry1 % id)
    try:
        site_res = cur.fetchone()
    except:
        return f"<h1>Invalid site label: {id}</h1>"
    cur.execute(qry2 % (id,dt))
    try:
        visit_res = cur.fetchone()
    except:
        return f"<h1>Invalid site label: {id}</h1>"
    cur.execute(qry3 % (id,dt))
    try:
        vars_res = cur.fetchall()
    except:
        return f"<h1>Invalid site label: {id}</h1>"
    cur.execute(qry4 % (id,dt))
    try:
        veg_res = cur.fetchone()
    except:
        return f"<h1>Invalid site label: {id}</h1>"

    cur.execute(qry5 % (id,dt))
    try:
        smp_res = cur.fetchone()
    except:
        return f"<h1>Invalid site label: {id}</h1>"

    cur.execute(qry6 % (id,dt))
    try:
        spp_res = cur.fetchall()
    except:
        return f"<h1>Invalid site label: {id}</h1>"

    cur.close()
    return render_template('visits/visit.html', site=id,visit=dt, siteinfo=site_res, visitinfo=visit_res, estvars=vars_res, veginfo=veg_res, smpinfo=smp_res, spplist=spp_res)
