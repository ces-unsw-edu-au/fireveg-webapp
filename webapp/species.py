from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db
from webapp.pg import get_pg_connection

from psycopg2.extras import DictCursor
import pandas as pd


from datetime import datetime, timedelta
import ipyplot
from dateutil.relativedelta import relativedelta
from pyinaturalist import (
    Observation,
    get_observations,
    pprint,
)
from rich import print

bp = Blueprint('species', __name__, url_prefix='/species')
create_spp_trait_table="""
CREATE TEMP TABLE species_traits (species_code,trait_codes) AS (
  WITH A AS (
    SELECT 'repr2' AS table_name, species_code FROM litrev.repr2
    UNION SELECT 'germ8' AS table_name, species_code FROM litrev.germ8
    UNION SELECT 'rect2' AS table_name, species_code FROM litrev.rect2
    UNION SELECT 'germ1' AS table_name, species_code FROM litrev.germ1
    UNION SELECT 'grow1' AS table_name, species_code FROM litrev.grow1
    UNION SELECT 'repr4' AS table_name, species_code FROM litrev.repr4
    UNION SELECT 'surv5' AS table_name, species_code FROM litrev.surv5
    UNION SELECT 'surv6' AS table_name, species_code FROM litrev.surv6
    UNION SELECT 'surv7' AS table_name, species_code FROM litrev.surv7
    UNION SELECT 'disp1' AS table_name, species_code FROM litrev.disp1
    UNION SELECT 'repr3' AS table_name, species_code FROM litrev.repr3a
    UNION SELECT 'repr3a' AS table_name, species_code FROM litrev.repr3
    UNION SELECT 'surv4' AS table_name, species_code FROM litrev.surv4
    UNION SELECT 'surv1' AS table_name, species_code FROM litrev.surv1
  )
  SELECT species_code,array_agg(table_name) FROM A GROUP BY species_code
);"""

@bp.route('/fam_list', methods=['GET', 'POST'])
@login_required
def fam_list():
    if request.method == 'GET':
        pg = get_pg_connection()
        cur = pg.cursor()
        cur.execute(create_spp_trait_table)

        cur.execute('SELECT family AS fam,count(distinct "speciesID"), count(distinct s.species_code), count(distinct q.species_code) FROM species.caps LEFT JOIN species_traits s ON "speciesCode_Synonym"=s.species_code::text LEFT JOIN form.quadrat_samples q ON "speciesCode_Synonym"=q.species_code::text  GROUP BY fam;')
        fam_list = cur.fetchall()
        cur.close()
        return render_template('species/fam-list.html', pairs=fam_list, the_title="Species per family")
    else:
        return redirect(url_for('.search_list', id=request.form['speciesname']))

@bp.route('/threat_list')
@login_required
def threat_list():
    pg = get_pg_connection()
    cur = pg.cursor()
    cur.execute(create_spp_trait_table)
    cur.execute('SELECT \"stateConservation\" AS fam,count(distinct "speciesID"), count(distinct s.species_code), count(distinct q.species_code) FROM species.caps LEFT JOIN species_traits s ON "speciesCode_Synonym"=s.species_code::text LEFT JOIN form.quadrat_samples q ON "speciesCode_Synonym"=q.species_code::text  GROUP BY fam;')
    fam_list = cur.fetchall()
    cur.execute('SELECT count(distinct "speciesID"), count(distinct s.species_code), count(distinct q.species_code) FROM species.caps LEFT JOIN species_traits s ON "speciesCode_Synonym"=s.species_code::text LEFT JOIN form.quadrat_samples q ON "speciesCode_Synonym"=q.species_code::text;')
    fam_total = cur.fetchall()
    cur.close()

    return render_template('species/threat-list.html', pairs=fam_list, ttl=fam_total, the_title="Species per family")

@bp.route('/family/<id>', methods=['GET', 'POST'])
@login_required
def sp_list(id):
    if request.method == 'GET':
        pg = get_pg_connection()
        cur = pg.cursor()
        cur.execute(create_spp_trait_table)
        cur.execute('SELECT "speciesID"::int AS id, "scientificName" AS name, "vernacularName" as vname,count(distinct s.species_code), count(distinct q.species_code), count(distinct q.visit_id),trait_codes FROM species.caps LEFT JOIN species_traits s ON "speciesCode_Synonym"=s.species_code::text LEFT JOIN form.quadrat_samples q ON "speciesCode_Synonym"=q.species_code::text WHERE "family"=%s GROUP BY id,name,vname,"sortOrder",trait_codes ORDER BY "sortOrder"', (id,))
        try:
            spp_qry = cur.fetchall()
        except:
            return render_template('invalid.html', type='family name', id=id)
        cur.close()
        return render_template('species/list.html', pairs=spp_qry, the_title=id)
    else:
        return redirect(url_for('.search_list', id=request.form['speciesname']))

@bp.route('/search/<id>', methods=['GET', 'POST'])
@login_required
def search_list(id):
    if request.method == 'GET':
        pg = get_pg_connection()
        cur = pg.cursor()
        cur.execute(create_spp_trait_table)
        cur.execute('SELECT "speciesID"::int AS id, "scientificName" AS name, "vernacularName" as vname,count(distinct s.species_code), count(distinct q.species_code), count(distinct q.visit_id),trait_codes FROM species.caps LEFT JOIN species_traits s ON "speciesCode_Synonym"=s.species_code::text LEFT JOIN form.quadrat_samples q ON "speciesCode_Synonym"=q.species_code::text WHERE ("scientificName" ILIKE %s OR "vernacularName" ILIKE %s) GROUP BY id,name,vname,"sortOrder",trait_codes ORDER BY "sortOrder"', (f'%%{id}%%', f'%%{id}%%'))
        try:
            spp_qry = cur.fetchall()
        except:
            return render_template('invalid.html', type='search', id=id)
        cur.close()
        return render_template('species/list.html', pairs=spp_qry, the_title=f'Search Results: {id}')
    else:
        return redirect(url_for('.search_list', id=request.form['speciesname']))

@bp.route('/category/<id>', methods=['GET', 'POST'])
@login_required
def cat_list(id):
    if request.method == 'GET':
        pg = get_pg_connection()
        cur = pg.cursor()
        cur.execute(create_spp_trait_table)
        cur.execute('SELECT "speciesID"::int AS id, "scientificName" AS name, "vernacularName" as vname,count(distinct s.species_code), count(distinct q.species_code), count(distinct q.visit_id),trait_codes FROM species.caps LEFT JOIN species_traits s ON "speciesCode_Synonym"=s.species_code::text LEFT JOIN form.quadrat_samples q ON "speciesCode_Synonym"=q.species_code::text WHERE "stateConservation"=%s GROUP BY id,name,vname,"sortOrder",trait_codes ORDER BY "sortOrder"', (id,))
        try:
            spp_qry = cur.fetchall()
        except:
            return render_template('invalid.html', type='category name', id=id)
        cur.close()
        return render_template('species/list.html', pairs=spp_qry, the_title=id)
    else:
        return redirect(url_for('.search_list', id=request.form['speciesname']))

@bp.route('/sp/<int:id>', methods=['GET', 'POST'])
@login_required
def sp_info(id):
    if request.method == 'GET':


        pg = get_pg_connection()
        cur = pg.cursor(cursor_factory=DictCursor)

        qry = "SELECT code,name, description, value_type, life_stage, life_history_process, category_vocabulary, method_vocabulary from litrev.trait_info;"
        cur.execute(qry)
        res = cur.fetchall()
        traitdata = pd.DataFrame(res,columns=['code','name', 'description', 'value_type', 'life_stage', 'life_history_process', 'category_vocabulary', 'method_vocabulary'])
        #fname='webapp/static/metadata/trait-description.csv'
        #traitdata = pd.read_csv(fname)
        synonym = request.args.get('synonym', default = 'valid', type = str)
        column = None
        if synonym != 'valid':
            column="speciesCode_Synonym"
        else:
            column="speciesID"
        qryspp=f"SELECT \"scientificName\", \"speciesID\"::int, family, \"taxonRank\", family, \"speciesCode_Synonym\", \"scientificNameAuthorship\", \"vernacularName\", \"establishmentMeans\", \"primaryGrowthFormGroup\", \"secondaryGrowthFormGroups\", \"stateConservation\", \"protectedInNSW\", \"countryConservation\", \"TSProfileID\" from species.caps WHERE \"{column}\"=%s"

        cur.execute(qryspp, (id,))
        try:
            spp_info = cur.fetchone()
        except:
            return render_template('invalid.html', type='species code', id=id)

        qrysmp="SELECT visit_id,visit_date,count(distinct sample_nr), species, species_code, seedbank, resprout_organ FROM form.quadrat_samples WHERE species_code=%s GROUP BY visit_id, visit_date, species, species_code, seedbank, resprout_organ ORDER BY visit_id,visit_date;"
        #if synonym == 'valid' and isinstance(spp_info[5],int):
        try:
            cur.execute(qrysmp, (spp_info[5],))
            samples = cur.fetchall()
        except:
            #samples = None # ? is this an option...
            return render_template('invalid.html', type='species code', id=spp_info[5])
        #elif synonym != 'valid':
        #    try:
        #        cur.execute(qrysmp, (id,))
        #        samples = cur.fetchall()
        #        except:
        #        return render_template('invalid.html', type='species code', id=id)
        #else:
        #    samples = None


        traits = list()

        for target in ('germ1','surv1','rect2','repr2','disp1','germ8','surv4'):
            qryresp=f"SELECT species, species_code, norm_value, main_source, count(record_id), sum(weight) as weight FROM litrev.{target} WHERE species_code=%s GROUP BY species, species_code, norm_value, main_source;"
            cur.execute(qryresp, (spp_info[5],))
            if cur.rowcount>0:
                entry = traitdata.loc[traitdata['code'] == target]
                entry.reset_index(drop=True, inplace=True)
                traits.append({
                "trait":target,
                "count":cur.rowcount,
                "list":cur.fetchall(),
                "metadata":entry.to_dict()
                })

        for target in ('repr3','repr3a','repr4','grow1','surv5','surv6','surv7'):
            qryresp=f"SELECT record_id, species, species_code, best, lower, upper, main_source FROM litrev.{target} WHERE species_code=%s;"
            cur.execute(qryresp, (spp_info[5],))
            if cur.rowcount>0:
                entry = traitdata.loc[traitdata['code'] == target]
                entry.reset_index(drop=True, inplace=True)
                traits.append({
                "trait":target,
                "count":cur.rowcount,
                "list":cur.fetchall(),
                "metadata":entry.to_dict()
                })

        qrylit1 = "SELECT * from litrev.ref_list where ref_code IN (SELECT distinct main_source FROM litrev.surv1 WHERE species_code=%s) OR ref_code IN (SELECT distinct main_source FROM litrev.repr3 WHERE species_code=%s)"
        qrylit2 = "SELECT * from litrev.ref_list where ref_code IN (SELECT distinct unnest(original_sources) FROM litrev.repr3 WHERE species_code=%s) OR ref_code IN (SELECT DISTINCT unnest(original_sources) FROM litrev.surv1 WHERE species_code=%s);"
        cur.execute(qrylit1,(spp_info[5],spp_info[5],))
        ref_list = cur.fetchall()
        cur.execute(qrylit2,(spp_info[5],spp_info[5],))
        add_list = cur.fetchall()

        qryvag = "SELECT persistence, rationale_persistence, status_persistence, establishment,status_establishment,date_updated FROM vag.va_groups where species_code=%s"
        cur.execute(qryvag,(spp_info[1],))
        vag_info = cur.fetchone()

        cur.close()

        raw_obs = get_observations(taxon_name=spp_info[0], per_page=1)
        iNobs = Observation.from_json_list(raw_obs)
        #images = [obs.photos[0].small_url for obs in iNobs[:3]]
        #labels = [str(obs) for obs in iNobs[:3]]

        return render_template('species/info.html', info=spp_info, inat_obs=iNobs, fsamp=samples, traits=traits, mainrefs=ref_list, addrefs=add_list, check=synonym, vag=vag_info)
    else:
        return redirect(url_for('.search_list', id=request.form['speciesname']))
