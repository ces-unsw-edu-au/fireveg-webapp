from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db
from webapp.pg import get_pg_connection

bp = Blueprint('species', __name__, url_prefix='/species')

@bp.route('/fam_list')
def fam_list():
    pg = get_pg_connection()
    cur = pg.cursor()
    cur.execute('SELECT "FamilyName" AS fam,count(*) FROM litrev.traits LEFT JOIN "Species_list" sp ON "SpeciesCode"=species_code GROUP BY fam;')
    fam_list = cur.fetchall()
    cur.close()
    return render_template('species/fam-list.html', pairs=fam_list, the_title="Species per family")

@bp.route('/family/<id>')
def sp_list(id):
    pg = get_pg_connection()
    cur = pg.cursor()
    cur.execute('SELECT "SpeciesCode"::int, "ScientificName", "CommonName" FROM litrev.traits LEFT JOIN "Species_list" sp ON "SpeciesCode"=species_code  WHERE "FamilyName"=\'%s\' ORDER BY "SortOrder"' % id)
    try:
        spp_qry = cur.fetchall()
    except:
        return f"<h1>Invalid family name: {id}</h1>"
    cur.close()
    return render_template('species/list.html', pairs=spp_qry, the_title=id)


@bp.route('/sp/<int:id>')
def sp_info(id):
    pg = get_pg_connection()
    cur = pg.cursor()
    cur.execute("SELECT species, species_code, resprouting, regenerative_organ, seedbank_type, postfire_seedling_recruitment FROM litrev.traits WHERE species_code='%s';" % id)
    try:
        site_qry = cur.fetchone()
    except:
        return f"<h1>Invalid site label: {id}</h1>"
    cur.close()
    return render_template('species/info.html', info=site_qry)
