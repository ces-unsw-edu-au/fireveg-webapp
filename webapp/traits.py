from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db
from webapp.pg import get_pg_connection

bp = Blueprint('traits', __name__, url_prefix='/traits')

@bp.route('/summary')
@login_required
def trait_sum():
    pg = get_pg_connection()
    cur = pg.cursor()
    cur.execute('select count(*), sum((resprouting is not null)::int), sum((regenerative_organ is not null)::int), sum((standing_plant_longevity is not null)::int), sum((seedbank_halflife is not null)::int) from litrev.survival_traits')
    trait_smr = cur.fetchone()
    cur.close()
    return render_template('traits/summary.html', surv_info=trait_smr, the_title="Summary of fire-related traits")


@bp.route('/<group>/<var>')
@login_required
def trait_list(group,var):
    pg = get_pg_connection()
    cur = pg.cursor()
    qry = 'SELECT species_code,species,\"speciesID\",{var} FROM litrev.{grp}_traits LEFT JOIN species.caps ON species_code::text="speciesCode_Synonym" WHERE {var} IS NOT NULL'.format(var=var,grp=group)
    cur.execute(qry)
    spp_list = cur.fetchall()
    cur.close()
    return render_template('traits/list.html', spps=spp_list,group=group,var=var)

#select regenerative_organ,count(*) from litrev.traits where regenerative_organ is not NULL group by regenerative_organ order by regenerative_organ;
