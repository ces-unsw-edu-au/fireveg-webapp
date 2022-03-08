from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db
from webapp.pg import get_pg_connection

import pandas as pd
from psycopg2.extras import DictCursor

bp = Blueprint('traits', __name__, url_prefix='/traits')

@bp.route('/summary')
@login_required
def trait_sum():
    fname='webapp/static/metadata/trait-description.csv'
    data = pd.read_csv(fname)
    first = data.loc[data.priority.notna()].sort_values(by='priority').fillna(0)
    data.set_index(['Trait code'], inplace=True)
    data.index.name=None
    fourth = data.loc[data.priority.isna()][['Trait name','Life stage','Life history process']]
    return render_template('traits/summary.html', tables=[fourth.to_html(classes='trait')],
    titles=['na', 'All other traits'],
    the_title="Summary of fire-related traits",
     column_names=first.columns.values, row_data=list(first.values.tolist()))

@bp.route('/<group>/<var>/values')
@login_required
def trait_list(group,var):
    pg = get_pg_connection()
    cur = pg.cursor()
    qry = 'SELECT species_code,species,\"speciesID\",{var} FROM {grp} LEFT JOIN species.caps ON species_code::text="speciesCode_Synonym" WHERE {var} IS NOT NULL'.format(var=var,grp=group)
    cur.execute(qry)
    spp_list = cur.fetchall()
    cur.close()
    return render_template('traits/list.html', spps=spp_list,group=group,var=var)


@bp.route('/<group>/<var>/info')
@login_required
def trait_info(group,var):
    pg = get_pg_connection()
    cur = pg.cursor(cursor_factory=DictCursor)

    qry = 'SELECT {var},count(DISTINCT species), count(DISTINCT \"speciesID\") FROM {grp} LEFT JOIN species.caps ON species_code::text="speciesCode_Synonym" GROUP BY {var}'.format(var=var,grp=group)
    cur.execute(qry)
    spp_list = cur.fetchall()

    qry = 'SELECT DISTINCT main_source, ref_cite, ref_code, alt_code FROM {grp} LEFT JOIN litrev.ref_list ON main_source=ref_code  '.format(grp=group)
    cur.execute(qry)
    ref_list = cur.fetchall()

    qry = 'SELECT ref_cite, ref_code, alt_code FROM litrev.ref_list WHERE ref_code IN (SELECT DISTINCT unnest(original_sources) as oref FROM {grp})'.format(grp=group)
    cur.execute(qry)
    add_list = cur.fetchall()

    cur.close()

    fname='webapp/static/metadata/trait-description.csv'
    data = pd.read_csv(fname)
    traitdata = data.loc[data.db_table == group]

    fname='webapp/static/metadata/trait-value-description.csv'
    data = pd.read_csv(fname)
    slcdata = data.loc[data.db_table == group][['value','description']]

    return render_template('traits/trait-info.html', spps=spp_list, mainrefs=ref_list, addrefs=add_list, group=group, var=var, trait=traitdata.values.tolist(), desc=list(slcdata.values.tolist()))

@bp.route('/<trait>/<code>')
@login_required
def spp(trait,code):
    pg = get_pg_connection()
    cur = pg.cursor(cursor_factory=DictCursor)

    if trait=='surv1':
        qry="SELECT * from litrev.resprouting where species_code='%s'"
        cur.execute(qry % code)
        rs = cur.fetchall()
    elif trait=='repr3':
        qry="SELECT * from litrev.firstflower where species_code='%s'"
        cur.execute(qry % code)
        rs = cur.fetchall()
    else:
        rs = None
    cur.close()
    return render_template('traits/spp.html', records=rs, species=code, trait=trait)
