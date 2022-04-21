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
    pg = get_pg_connection()
    cur = pg.cursor(cursor_factory=DictCursor)
    qry = "SELECT code, name, life_stage, life_history_process, priority,value_type FROM litrev.trait_info ORDER BY code"
    cur.execute(qry)
    res = cur.fetchall()
    cur.close()
    data = pd.DataFrame(res)
    data = data.rename(columns={0:"Trait code", 1:"Trait name", 2:"Life stage", 3:"Life history process", 4:"priority", 5:"value_type"})

    # Trait code,Trait name,Life stage,Life history process,priority,db_table,db_column,status,import
    #fname='webapp/static/metadata/trait-description.csv'
    #data = pd.read_csv(fname)
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


@bp.route('/QA/<trait>')
@login_required
def trait_qa(trait):
    valuetype = request.args.get('valuetype', default = 'categorical', type = str)

    pg = get_pg_connection()
    cur = pg.cursor(cursor_factory=DictCursor)
    if valuetype == 'categorical':
        qry = 'select distinct main_source,raw_value,count(*) from litrev.{} WHERE norm_value is NULL group by main_source,raw_value,norm_value ;'.format(trait)
    else:
        qry = 'select distinct main_source,raw_value,count(*) from litrev.{} WHERE best is NULL AND lower is NULL and upper is NULL group by main_source,raw_value ;'.format(trait)
    cur.execute(qry)
    res = cur.fetchall()
    cur.close()
    return render_template('traits/QA.html', result=res, trait=trait)


@bp.route('/QA/<trait>/<kwd>')
@login_required
def trait_kwds(trait,kwd):
    pg = get_pg_connection()
    cur = pg.cursor(cursor_factory=DictCursor)
    qry = "select species, species_code, raw_value, norm_value, original_notes from litrev.{} WHERE '{}'=ANY(raw_value) ;".format(trait,kwd)
    cur.execute(qry)
    res = cur.fetchall()
    cur.close()
    return render_template('traits/kwd.html', result=res, trait=trait, kwd=kwd)

@bp.route('/<group>/<var>/info')
@login_required
def trait_info(group,var):
    pg = get_pg_connection()
    cur = pg.cursor(cursor_factory=DictCursor)

    if var == 'best':
        qry = 'SELECT (best is not NULL OR lower IS NOT NULL OR upper IS NOT NULL) as var,count(DISTINCT species) as nspp, count(DISTINCT \"speciesID\") as ncode FROM litrev.{grp} LEFT JOIN species.caps ON species_code::text="speciesCode_Synonym"  GROUP BY var '.format(grp=group)
    else:
        qry = 'SELECT {var} as var,count(DISTINCT species) as nspp, count(DISTINCT \"speciesID\") as ncode FROM litrev.{grp} LEFT JOIN species.caps ON species_code::text="speciesCode_Synonym" GROUP BY {var}'.format(var=var,grp=group)

    cur.execute(qry)
    spp_list = cur.fetchall()

    qry = 'SELECT DISTINCT main_source, ref_cite, ref_code, alt_code FROM litrev.{grp} LEFT JOIN litrev.ref_list ON main_source=ref_code  WHERE main_source is NOT NULL;'.format(grp=group)
    cur.execute(qry)
    ref_list = cur.fetchall()

    qry = 'SELECT ref_cite, ref_code, alt_code FROM litrev.ref_list WHERE ref_code IN (SELECT DISTINCT unnest(original_sources) as oref FROM litrev.{grp} WHERE original_sources IS NOT NULL) ORDER BY ref_cite;'.format(grp=group)
    cur.execute(qry)
    add_list = cur.fetchall()

    qry = "SELECT * from litrev.trait_info where code='{}';".format(group)
    cur.execute(qry)
    traitdata = cur.fetchone()

    if traitdata['category_vocabulary'] is not None:
        qry="SELECT pg_catalog.obj_description(t.oid, 'pg_type')::json from pg_type t where typname = '{}';".format(traitdata['category_vocabulary'])
    else:

        qry="SELECT (SELECT pg_catalog.col_description(c.oid, cols.ordinal_position::int) FROM pg_catalog.pg_class c WHERE c.oid     = (SELECT CONCAT(cols.table_schema,'.',cols.table_name)::regclass::oid) AND c.relname = cols.table_name)::json  as column_comment FROM information_schema.columns cols WHERE cols.table_catalog = 'dbfireveg' AND cols.table_schema  = 'litrev' AND cols.table_name    = '{}' AND cols.column_name    = 'best';  ".format(group)
    cur.execute(qry)
    slcdata = cur.fetchone()

    cur.close()

    #fname='webapp/static/metadata/trait-description.csv'
    #data = pd.read_csv(fname)
    #traitdata = data.loc[data.db_table == group]

    #fname='webapp/static/metadata/trait-value-description.csv'
    #data = pd.read_csv(fname)
    #slcdata = data.loc[data.db_table == group][['value','description']]

    return render_template('traits/trait-info.html', spps=spp_list, mainrefs=ref_list, addrefs=add_list, group=group, var=var, trait=traitdata, desc=slcdata[0])

@bp.route('/<trait>/<code>')
@login_required
def spp(trait,code):
    pg = get_pg_connection()
    cur = pg.cursor(cursor_factory=DictCursor)

    qry="SELECT * from litrev.{table} where species_code='{spcode}'"
    cur.execute(qry.format(table=trait,spcode=code))
    rs = cur.fetchall()
    cur.close()
    return render_template('traits/spp.html', records=rs, species=code, trait=trait)
