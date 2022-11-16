from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db
from webapp.pg import get_pg_connection

import re
import pandas as pd
from psycopg2.extras import DictCursor

# this is for when user input needs to define a column or table
# restrict to only allow alphanumeric characters to avoid SQL injection
userInputRe = re.compile('^[A-Za-z0-9]+$')
def isSaneUserInput(input):
    return userInputRe.match(input)

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
    if not isSaneUserInput(group):
        return render_template('invalid.html', type='user input', id=group)
    if not isSaneUserInput(var):
        return render_template('invalid.html', type='user input', id=var)
    pg = get_pg_connection()
    cur = pg.cursor()
    qry = f'SELECT species_code,species,\"speciesID\",{var} FROM {group} LEFT JOIN species.caps ON species_code::text="speciesCode_Synonym" WHERE {var} IS NOT NULL'
    cur.execute(qry)
    spp_list = cur.fetchall()
    cur.close()
    return render_template('traits/list.html', spps=spp_list,group=group,var=var)


@bp.route('/QA/<trait>')
@login_required
def trait_qa(trait):
    if not isSaneUserInput(trait):
        return render_template('invalid.html', type='user input', id=trait)
    valuetype = request.args.get('valuetype', default = 'categorical', type = str)

    pg = get_pg_connection()
    cur = pg.cursor(cursor_factory=DictCursor)
    if valuetype == 'categorical':
        qry = f'select distinct main_source,raw_value,count(*) from litrev.{trait} WHERE norm_value is NULL group by main_source,raw_value,norm_value ;'
    else:
        qry = f'select distinct main_source,raw_value,count(*) from litrev.{trait} WHERE best is NULL AND lower is NULL and upper is NULL group by main_source,raw_value ;'
    cur.execute(qry)
    res = cur.fetchall()
    cur.close()
    return render_template('traits/QA.html', result=res, trait=trait)


@bp.route('/QA/<trait>/<kwd>')
@login_required
def trait_kwds(trait,kwd):
    if not isSaneUserInput(trait):
        return render_template('invalid.html', type='user input', id=trait)
    valuetype = request.args.get('valuetype', default = 'categorical', type = str)

    pg = get_pg_connection()
    cur = pg.cursor(cursor_factory=DictCursor)
    if valuetype == 'categorical':
        qry = f"select species, species_code, raw_value, norm_value, original_notes from litrev.{trait} WHERE %s=ANY(raw_value) ;"
    else:
        qry = f"select species, species_code, raw_value, best as norm_value, original_notes from litrev.{trait} WHERE %s=ANY(raw_value) ;"
    cur.execute(qry, (kwd,))
    res = cur.fetchall()
    cur.close()
    return render_template('traits/kwd.html', result=res, trait=trait, kwd=kwd)

@bp.route('/<group>/<var>/info')
@login_required
def trait_info(group,var):
    if not isSaneUserInput(group):
        return render_template('invalid.html', type='user input', id=group)
    pg = get_pg_connection()
    cur = pg.cursor(cursor_factory=DictCursor)

    if var in ('best','numerical'):
        qry = f'SELECT (best is not NULL OR lower IS NOT NULL OR upper IS NOT NULL) as var,count(DISTINCT species) as nspp, count(DISTINCT \"speciesID\") as ncode FROM litrev.{group} LEFT JOIN species.caps ON species_code::text="speciesCode_Synonym"  GROUP BY var '
    else:
        qry = f'SELECT norm_value as var,count(DISTINCT species) as nspp, count(DISTINCT \"speciesID\") as ncode FROM litrev.{group} LEFT JOIN species.caps ON species_code::text="speciesCode_Synonym" GROUP BY norm_value'

    cur.execute(qry)
    spp_list = cur.fetchall()


    qry=f"SELECT count(record_id) as total,ref_cite, ref_code FROM litrev.{group} LEFT JOIN litrev.ref_list ON main_source=ref_code  WHERE main_source is NOT NULL GROUP BY ref_code,ref_cite "
    cur.execute(qry)
    ref_list = cur.fetchall()

    qry = f'SELECT ref_cite, ref_code, alt_code FROM litrev.ref_list WHERE ref_code IN (SELECT DISTINCT unnest(original_sources) as oref FROM litrev.{group} WHERE original_sources IS NOT NULL) ORDER BY ref_cite;'
    cur.execute(qry)
    add_list = cur.fetchall()

    qry = "SELECT * from litrev.trait_info where code=%s;"
    cur.execute(qry, (group,))
    traitdata = cur.fetchone()

    if traitdata['category_vocabulary'] is not None:
        qry="SELECT pg_catalog.obj_description(t.oid, 'pg_type')::json from pg_type t where typname = %s;"
        cur.execute(qry, (traitdata['category_vocabulary'],))
    else:
        qry="SELECT (SELECT pg_catalog.col_description(c.oid, cols.ordinal_position::int) FROM pg_catalog.pg_class c WHERE c.oid     = (SELECT CONCAT(cols.table_schema,'.',cols.table_name)::regclass::oid) AND c.relname = cols.table_name)::json  as column_comment FROM information_schema.columns cols WHERE cols.table_catalog = 'dbfireveg' AND cols.table_schema  = 'litrev' AND cols.table_name    = %s AND cols.column_name    = 'best';  "
        cur.execute(qry, (group,))
    slcdata = cur.fetchone()

    if traitdata['method_vocabulary'] is not None:
        qry="SELECT pg_catalog.obj_description(t.oid, 'pg_type')::json from pg_type t where typname = %s;"
        cur.execute(qry, (traitdata['method_vocabulary'],))
        mtds = cur.fetchone()
    else:
        mtds = None
    cur.close()

    return render_template('traits/trait-info.html', spps=spp_list, mainrefs=ref_list, addrefs=add_list, group=group, var=var, trait=traitdata, desc=slcdata[0], methods=mtds)

@bp.route('/<trait>/<code>')
@login_required
def spp(trait,code):
    if not isSaneUserInput(trait):
        return render_template('invalid.html', type='user input', id=trait)
    pg = get_pg_connection()
    cur = pg.cursor(cursor_factory=DictCursor)

    qry=f"SELECT * from litrev.{trait} where species_code=%s"
    cur.execute(qry, (code,))
    rs = cur.fetchall()
    cur.close()
    return render_template('traits/spp.html', records=rs, species=code, trait=trait)


@bp.route('/VA')
@login_required
def va_groups():
    pg = get_pg_connection()
    cur = pg.cursor(cursor_factory=DictCursor)
    qry = "SELECT rationale_persistence, persistence, count(*) FROM vag.va_groups GROUP BY rationale_persistence, persistence ORDER BY cardinality(rationale_persistence);"
    cur.execute(qry)
    dectree = cur.fetchall()


    qry = "select unnest(persistence) p, unnest(establishment) as e, count(distinct species_code) from vag.va_groups group by p, e ORDER BY p,e"
    cur.execute(qry)
    res = cur.fetchall()
    df = pd.DataFrame(res)
    df=df.rename(columns={0:"Persistence",1:"Establishment",2:"Records"})
    df['Records'] = df['Records'].astype(int)
    tbl=df.pivot(index='Persistence', columns='Establishment', values='Records')
    tbl.fillna(0,inplace=True)

    cur.close()

    return render_template('traits/VA.html', persistence=dectree,rows=tbl.index.values, cols=tbl.columns.values, cats=tbl.astype(int).values.tolist())
