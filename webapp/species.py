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
    cur.execute('SELECT family AS fam,count(distinct "speciesID"),count(distinct s.species_code) FROM species.caps LEFT JOIN litrev.survival_traits s ON "speciesCode_Synonym"=species_code::text GROUP BY fam;')
    fam_list = cur.fetchall()
    cur.close()
    return render_template('species/fam-list.html', pairs=fam_list, the_title="Species per family")

@bp.route('/family/<id>')
def sp_list(id):
    pg = get_pg_connection()
    cur = pg.cursor()
    cur.execute('SELECT "speciesID"::int AS id, "scientificName" AS name, "vernacularName" as vname,count(distinct s.species_code) FROM species.caps LEFT JOIN litrev.survival_traits s ON "speciesCode_Synonym"=species_code::text WHERE "family"=\'%s\' GROUP BY id,name,vname,"sortOrder" ORDER BY "sortOrder"' % id)
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

    qryspp="SELECT \"scientificName\", \"speciesID\"::int, family, \"taxonRank\", family, \"speciesCode_Synonym\", \"scientificNameAuthorship\", \"vernacularName\", \"establishmentMeans\", \"primaryGrowthFormGroup\", \"secondaryGrowthFormGroups\", \"stateConservation\", \"protectedInNSW\", \"countryConservation\" from species.caps WHERE \"speciesID\"=%s;"
    cur.execute(qryspp % (id))
    try:
        spp_info = cur.fetchone()
    except:
        return f"<h1>Invalid species code: {id}</h1>"

    qrysurv="SELECT species, species_code, resprouting, regenerative_organ, standing_plant_longevity, seedbank_halflife, seed_longevity FROM litrev.survival_traits WHERE species_code=%s;"
    cur.execute(qrysurv % spp_info[5])
    try:
        surv_trts = cur.fetchall()
    except:
        return f"<h1>Invalid species code: {id}</h1>"

    qrysurv="SELECT species, species_code, resprouting, regenerative_organ, standing_plant_longevity, seedbank_halflife, seed_longevity FROM litrev.survival_traits WHERE species_code=%s;"
    cur.execute(qrysurv % spp_info[5])
    try:
        surv_trts = cur.fetchall()
    except:
        return f"<h1>Invalid species code: {id}</h1>"

    cur.close()
    return render_template('species/info.html', info=spp_info,survs=surv_trts)
