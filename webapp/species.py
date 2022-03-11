from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db
from webapp.pg import get_pg_connection

from psycopg2.extras import DictCursor
import pandas as pd

bp = Blueprint('species', __name__, url_prefix='/species')

@bp.route('/fam_list')
@login_required
def fam_list():
    pg = get_pg_connection()
    cur = pg.cursor()
    cur.execute('SELECT family AS fam,count(distinct "speciesID"), count(distinct s.species_code), count(distinct q.species_code) FROM species.caps LEFT JOIN litrev.surv1 s ON "speciesCode_Synonym"=s.species_code::text LEFT JOIN form.quadrat_samples q ON "speciesCode_Synonym"=q.species_code::text  GROUP BY fam;')
    fam_list = cur.fetchall()
    cur.close()
    return render_template('species/fam-list.html', pairs=fam_list, the_title="Species per family")

@bp.route('/threat_list')
@login_required
def threat_list():
    pg = get_pg_connection()
    cur = pg.cursor()
    cur.execute('SELECT \"stateConservation\" AS fam,count(distinct "speciesID"), count(distinct s.species_code), count(distinct q.species_code) FROM species.caps LEFT JOIN litrev.surv1 s ON "speciesCode_Synonym"=s.species_code::text LEFT JOIN form.quadrat_samples q ON "speciesCode_Synonym"=q.species_code::text  GROUP BY fam;')
    fam_list = cur.fetchall()
    cur.close()
    return render_template('species/threat-list.html', pairs=fam_list, the_title="Species per family")

@bp.route('/family/<id>')
@login_required
def sp_list(id):
    pg = get_pg_connection()
    cur = pg.cursor()
    cur.execute('SELECT "speciesID"::int AS id, "scientificName" AS name, "vernacularName" as vname,count(distinct s.species_code), count(distinct q.species_code), count(distinct q.visit_id) FROM species.caps LEFT JOIN litrev.surv1 s ON "speciesCode_Synonym"=s.species_code::text LEFT JOIN form.quadrat_samples q ON "speciesCode_Synonym"=q.species_code::text WHERE "family"=\'%s\' GROUP BY id,name,vname,"sortOrder" ORDER BY "sortOrder"' % id)
    try:
        spp_qry = cur.fetchall()
    except:
        return f"<h1>Invalid family name: {id}</h1>"
    cur.close()
    return render_template('species/list.html', pairs=spp_qry, the_title=id)

@bp.route('/category/<id>')
@login_required
def cat_list(id):
    pg = get_pg_connection()
    cur = pg.cursor()
    cur.execute('SELECT "speciesID"::int AS id, "scientificName" AS name, "vernacularName" as vname,count(distinct s.species_code), count(distinct q.species_code), count(distinct q.visit_id) FROM species.caps LEFT JOIN litrev.surv1 s ON "speciesCode_Synonym"=s.species_code::text LEFT JOIN form.quadrat_samples q ON "speciesCode_Synonym"=q.species_code::text WHERE "stateConservation"=\'%s\' GROUP BY id,name,vname,"sortOrder" ORDER BY "sortOrder"' % id)
    try:
        spp_qry = cur.fetchall()
    except:
        return f"<h1>Invalid category name: {id}</h1>"
    cur.close()
    return render_template('species/list.html', pairs=spp_qry, the_title=id)

@bp.route('/sp/<int:id>')
@login_required
def sp_info(id):

    fname='webapp/static/metadata/trait-description.csv'
    traitdata = pd.read_csv(fname)

    pg = get_pg_connection()
    cur = pg.cursor(cursor_factory=DictCursor)

    qryspp="SELECT \"scientificName\", \"speciesID\"::int, family, \"taxonRank\", family, \"speciesCode_Synonym\", \"scientificNameAuthorship\", \"vernacularName\", \"establishmentMeans\", \"primaryGrowthFormGroup\", \"secondaryGrowthFormGroups\", \"stateConservation\", \"protectedInNSW\", \"countryConservation\" from species.caps WHERE \"speciesID\"=%s;"
    cur.execute(qryspp % (id))
    try:
        spp_info = cur.fetchone()
    except:
        return f"<h1>Invalid species code: {id}</h1>"

    qrysmp="SELECT visit_id,visit_date,count(distinct sample_nr), species, species_code, seedbank, resprout_organ FROM form.quadrat_samples WHERE species_code=%s GROUP BY visit_id, visit_date, species, species_code, seedbank, resprout_organ ORDER BY visit_id,visit_date;"
    cur.execute(qrysmp % spp_info[5])
    try:
        samples = cur.fetchall()
    except:
        return f"<h1>Invalid species code: {id}</h1>"

    traits = list()

    for target in ('surv1','rect2','repr2'):
        qryresp="SELECT species, species_code, norm_value, main_source, count(record_id), sum(weight) as weight FROM litrev.{table} WHERE species_code='{code}' GROUP BY species, species_code, norm_value, main_source;"
        cur.execute(qryresp.format(table=target,code=spp_info[5]))
        if cur.rowcount>0:
            entry = traitdata.loc[traitdata['Trait code'] == target]
            entry.reset_index(drop=True, inplace=True)
            traits.append({
            "trait":target,
            "count":cur.rowcount,
            "list":cur.fetchall(),
            "metadata":entry.to_dict()
            })

    for target in ('repr3','repr3a'):
        qryresp="SELECT record_id, species, species_code, best, lower, upper, main_source FROM litrev.{table} WHERE species_code='{code}';"
        cur.execute(qryresp.format(table=target,code=spp_info[5]))
        if cur.rowcount>0:
            entry = traitdata.loc[traitdata['Trait code'] == target]
            entry.reset_index(drop=True, inplace=True)
            traits.append({
            "trait":target,
            "count":cur.rowcount,
            "list":cur.fetchall(),
            "metadata":entry.to_dict()
            })

    qrylit1 = "SELECT * from litrev.ref_list where ref_code IN (SELECT distinct main_source FROM litrev.surv1 WHERE species_code='{spcode}') OR ref_code IN (SELECT distinct main_source FROM litrev.repr3 WHERE species_code='{spcode}')"
    qrylit2 = "SELECT * from litrev.ref_list where ref_code IN (SELECT distinct unnest(original_sources) FROM litrev.repr3 WHERE species_code='{spcode}') OR ref_code IN (SELECT DISTINCT unnest(original_sources) FROM litrev.surv1 WHERE species_code='{spcode}');"
    cur.execute(qrylit1.format(spcode=spp_info[5]))
    ref_list = cur.fetchall()
    cur.execute(qrylit2.format(spcode=spp_info[5]))
    add_list = cur.fetchall()

    cur.close()
    return render_template('species/info.html', info=spp_info, fsamp=samples, traits=traits, mainrefs=ref_list, addrefs=add_list)
