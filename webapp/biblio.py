from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db
from webapp.pg import get_pg_connection

from psycopg2.extras import DictCursor

bp = Blueprint('biblio', __name__, url_prefix='/references')


@bp.route('/ref_list')
@login_required
def ref_list():
    pg = get_pg_connection()
    cur = pg.cursor(cursor_factory=DictCursor)
    cur.execute('WITH a AS (select unnest(original_sources) as oref, COUNT(DISTINCT species_code) as nspp from litrev.resprouting group by oref), b AS (SELECT main_source as mref, COUNT(DISTINCT species_code) as nspp FROM litrev.resprouting GROUP BY mref) SELECT ref_code, ref_cite, alt_code, a.nspp as nspp, b.nspp as ispp FROM litrev.ref_list LEFT JOIN a ON a.oref=alt_code LEFT JOIN b ON b.mref=ref_code ORDER BY ref_code;')
    ref_list = cur.fetchall()
    cur.close()
    return render_template('biblio/ref-list.html', refs=ref_list, the_title="All References")


@bp.route('/ref_info/<id>')
@login_required
def ref_info(id):
    qry1 = "SELECT ref_code, ref_cite, alt_code FROM litrev.ref_list WHERE ref_code='%s'"
    qry2 = "SELECT record_id, species, species_code,\"speciesID\"::int as species_id FROM litrev.firstflower LEFT JOIN species.caps ON species_code=\"speciesCode_Synonym\" WHERE main_source='{ref}' OR '{ref}'=ANY(original_sources) ORDER BY random()"
    qry3 = "SELECT record_id, species, species_code,\"speciesID\"::int as species_id FROM litrev.resprouting LEFT JOIN species.caps ON species_code=\"speciesCode_Synonym\" WHERE main_source='{ref}' OR '{ref}'=ANY(original_sources) ORDER BY random()"
    pg = get_pg_connection()
    cur = pg.cursor(cursor_factory=DictCursor)
    cur.execute(qry1 % id)
    ref_info = cur.fetchone()
    cur.execute(qry2.format(ref=id))
    trait_repr3 = cur.fetchmany(10)
    cur.execute(qry3.format(ref=id))
    trait_surv1 = cur.fetchmany(10)
    cur.close()
    return render_template('biblio/ref-info.html', repr3=trait_repr3, surv1=trait_surv1, ref=ref_info)


#select distinct species_code,species from litrev.resprouting where main_source='Department of Natural Resources & Environment (Vic' OR 'Department of Natural Resources & Environment (Vic'=any(original_sources);
