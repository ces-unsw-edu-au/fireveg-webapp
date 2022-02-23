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
def ref_list():
    pg = get_pg_connection()
    cur = pg.cursor(cursor_factory=DictCursor)
    cur.execute('WITH a AS (select unnest(original_sources) as oref, COUNT(DISTINCT species_code) as nspp from litrev.resprouting group by oref), b AS (SELECT main_source as mref, COUNT(DISTINCT species_code) as nspp FROM litrev.resprouting GROUP BY mref) SELECT ref_code, ref_cite, alt_code, a.nspp as nspp, b.nspp as ispp FROM litrev.ref_list LEFT JOIN a ON a.oref=alt_code LEFT JOIN b ON b.mref=ref_code ORDER BY ref_code;')
    ref_list = cur.fetchall()
    cur.close()
    return render_template('biblio/ref-list.html', refs=ref_list, the_title="All References")


#select distinct species_code,species from litrev.resprouting where main_source='Department of Natural Resources & Environment (Vic' OR 'Department of Natural Resources & Environment (Vic'=any(original_sources);
