from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db
from webapp.pg import get_pg_connection

bp = Blueprint('traits', __name__, url_prefix='/traits')

@bp.route('/summary')
def trait_sum():
    pg = get_pg_connection()
    cur = pg.cursor()
    cur.execute('select count(*), sum((resprouting is not null)::int), sum((regenerative_organ is not null)::int), sum((seedbank_type is not null)::int), sum((postfire_seedling_recruitment is not null)::int) from litrev.traits')
    trait_smr = cur.fetchone()
    cur.close()
    return render_template('traits/summary.html', info=trait_smr, the_title="Summary of fire-related traits")


#select regenerative_organ,count(*) from litrev.traits where regenerative_organ is not NULL group by regenerative_organ order by regenerative_organ;
