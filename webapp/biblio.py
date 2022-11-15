from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db
from webapp.pg import get_pg_connection

from psycopg2.extras import DictCursor
import pandas as pd

bp = Blueprint('biblio', __name__, url_prefix='/references')


@bp.route('/ref_list')
@login_required
def ref_list():
    pg = get_pg_connection()
    cur = pg.cursor(cursor_factory=DictCursor)
    cur.execute('WITH a AS (select unnest(original_sources) as oref, COUNT(DISTINCT species_code) as nspp from litrev.surv1 group by oref), b AS (SELECT main_source as mref, COUNT(DISTINCT species_code) as nspp FROM litrev.surv1 GROUP BY mref) SELECT ref_code, ref_cite, alt_code, a.nspp as nspp, b.nspp as ispp FROM litrev.ref_list LEFT JOIN a ON a.oref=alt_code LEFT JOIN b ON b.mref=ref_code ORDER BY ref_code;')
    ref_list = cur.fetchall()
    cur.close()
    return render_template('biblio/ref-list.html', refs=ref_list, the_title="All References")


@bp.route('/ref_info/<id>')
@login_required
def ref_info(id):

    fname='webapp/static/metadata/trait-description.csv'
    traitdata = pd.read_csv(fname)

    qry1 = "SELECT ref_code, ref_cite, alt_code FROM litrev.ref_list WHERE ref_code=%s"
    qry2 = "SELECT species, species_code, \"speciesID\"::int as species_id FROM litrev.{table} LEFT JOIN species.caps ON species_code=\"speciesCode_Synonym\" WHERE main_source=%s OR %s=ANY(original_sources) GROUP BY species, species_code, species_id ORDER BY random()"

    pg = get_pg_connection()
    cur = pg.cursor(cursor_factory=DictCursor)
    cur.execute(qry1, (id,))
    ref_info = cur.fetchone()

    traits = list()

    for target in ('surv1','surv4','surv5','surv6','surv7','grow1','germ1','germ8','repr3','repr3a','repr4','rect2','repr2'):
        cur.execute(qry2.format(table=target), (id, id,))
        if cur.rowcount>0:
            entry = traitdata.loc[traitdata['Trait code'] == target]
            entry.reset_index(drop=True, inplace=True)
            traits.append({
            "trait":target,
            "count":cur.rowcount,
            "list":cur.fetchmany(10),
            "metadata":entry.to_dict()
            })


    return render_template('biblio/ref-info.html', ref=ref_info, traits=traits)


#select distinct species_code,species from litrev.surv1 where main_source='Department of Natural Resources & Environment (Vic' OR 'Department of Natural Resources & Environment (Vic'=any(original_sources);
