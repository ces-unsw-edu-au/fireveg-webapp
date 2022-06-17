from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_file
)
import pandas as pd
import io

from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db
from webapp.xlfile import create_output_xl
from webapp.pg import get_pg_connection
from psycopg2.extras import DictCursor

bp = Blueprint('dataexport', __name__, url_prefix='/data-xport')

## queries: ## test with -- WHERE species ilike '%euca%' and
qryCategorical= """
SELECT "currentScientificName" as spp, "currentScientificNameCode" as sppcode,
    array_agg(species) as nspp,
    array_agg(norm_value::text) as val,array_agg(weight) as w,
    array_agg(main_source) as refs,
    array_accum(original_sources) as orefs

FROM litrev.{}
LEFT JOIN species.caps
ON species_code="speciesCode_Synonym"
WHERE species ilike '%euca%' and "currentScientificName" is not NULL AND weight>0 AND main_source is not NULL
GROUP BY spp,sppcode;
"""

qryNumeric= """
SELECT "currentScientificName" as spp, "currentScientificNameCode" as sppcode,
array_agg(species) as nspp,
array_agg(best) as best,array_agg(lower) as lower,array_agg(upper) as upper,array_agg(weight) as w,
array_agg(main_source) as refs,
array_accum(original_sources) as orefs
FROM litrev.{}
LEFT JOIN species.caps
ON species_code="speciesCode_Synonym"
WHERE species ilike '%euca%' and "currentScientificName" is not NULL AND weight>0
GROUP BY spp,sppcode;
"""

## functions

def summarise_values(x,w):
    if None in x:
        sfx = " * "
    else:
        sfx = ""
    df=pd.concat({"value": pd.Series(x),"weight": pd.Series(w)},axis=1)
    res = df.groupby(by="value").sum() / df.weight.sum()
    res = res.sort_values(by="weight",ascending=[0])
    val = ""
    glue = ""
    for index, row in res.iterrows():
        if row['weight'] > 0.1:
            val = val + glue + index
            glue = " / "
        elif row['weight'] > 0.05:
            val = val + glue + ("(%s)" % index)
            glue = " / "
        else:
            val = val + glue + ("[%s]" % index)
            glue = " / "
    return (val + sfx).strip(" ")

def summarise_triplet(x,y,z,w):
    df=pd.concat({"best": pd.Series(x),"lower": pd.Series(y),"upper": pd.Series(z),"weight": pd.Series(w)},axis=1)
    val="%0.1f (%0.1f -- %0.1f)" % (df['best'].mean(),df['lower'].min(),df['upper'].max())
    if val=="nan (nan -- nan)":
        val="*"
    elif val.find("nan")==0:
        val=val.replace("nan (","(")
    elif val.find("nan")>0:
        val=val.replace(" (nan -- nan)","")
    if val.find("nan")>0:
        val=val.replace("nan","?")
    return val


## create and download excel file for data export:

@bp.route('/download', methods=('GET', 'POST'))
@login_required
def download_file():
    if request.method == 'POST':
        response = request.form

        pg = get_pg_connection()
        cur = pg.cursor(cursor_factory=DictCursor)

        for trait in ['surv1','surv4','repr2','rect2','disp1','germ1','germ8']:
            cur.execute(qryCategorical.format(trait))
            res = cur.fetchall()
            df1 = pd.DataFrame(res)
            col1="%s.txn" % trait
            col2="%s.v" % trait
            col3="%s.w" % trait
            col4="%s.mref" % trait
            col5="%s.oref" % trait

            df1=df1.rename(columns={0:"Species",1:"Code",2:col1,3:col2,4:col3,5:col4,6:col5})
            df1[trait]=df1.apply(lambda row : summarise_values(row[col2],row[col3]), axis = 1)
            if trait == 'surv1':
                df = df1
            else:
                df = pd.merge(df, df1, on = ["Species","Code"], how = "outer").sort_values(by="Species",ascending=[1])


        for trait in ['repr3','repr3a','repr4',]:
            cur.execute(qryNumeric.format(trait))
            res = cur.fetchall()
            if len(res)>0:
                df1 = pd.DataFrame(res)
                col1="%s.txn" % trait
                col2="%s.best" % trait
                col3="%s.lower" % trait
                col4="%s.upper" % trait
                col5="%s.w" % trait
                col6="%s.mref" % trait
                col7="%s.oref" % trait

                df1=df1.rename(columns={0:"Species",1:"Code",2:col1,3:col2,4:col3,5:col4,6:col5,7:col6,8:col7})
                df1[trait]=df1.apply(lambda row : summarise_triplet(row[col2],row[col3],row[col4],row[col5]), axis = 1)
                df = pd.merge(df, df1, on = ["Species","Code"], how = "outer").sort_values(by="Species",ascending=[1])

        ## this references df, so we need it here:
        def unique_taxa(row,slc):
            ss=[col.find(slc)>0 for col in df.loc[1].index.tolist()]
            record=row[ss]
            records=record.values.tolist()
            valid=list()
            for x in records:
                if type(x)==list:
                    valid=valid+x
            z=list(set(valid))
            z="; ".join(z)
            return(z)

        df['orig_species']=df.apply(lambda row : unique_taxa(row,'txn'), axis = 1)
        df['main_refs']=df.apply(lambda row : unique_taxa(row,'mref'), axis = 1)
        df['orig_refs']=df.apply(lambda row : unique_taxa(row,'oref'), axis = 1)
        df[['orig_species','main_refs','orig_refs']]

        ## this references df, so we need it here:
        def extract_refs(row,slc):
            ss=[col.find(slc)>0 for col in df.loc[1].index.tolist()]
            record=row[ss]
            records=record.values.tolist()
            valid=list()
            for x in records:
                if type(x)==list:
                    valid=valid+x
            z=list(set(valid))
            return(z)

        refs=df.apply(lambda row : extract_refs(row,'mref'), axis = 1)
        valid_refs=list()
        for x in refs:
            if type(x)==list:
                valid_refs=valid_refs+x

        refs=df.apply(lambda row : extract_refs(row,'oref'), axis = 1)
        for x in refs:
            if type(x)==list:
                valid_refs=valid_refs+x

        valid_refs=tuple(set(valid_refs))

        cur.execute("SELECT ref_code,ref_cite FROM litrev.ref_list WHERE ref_code IN %s ORDER BY ref_code",(valid_refs,))
        ref_info = cur.fetchall()


        cur.execute("SELECT code,name,description,value_type,life_stage,life_history_process,priority FROM litrev.trait_info ORDER BY code")
        trait_info = cur.fetchall()

        cur.close()

        wb = create_output_xl(traitsummary=df, referencelist=ref_info, traitlist=trait_info)
        excel_stream = io.BytesIO()
        wb.save(excel_stream)
        excel_stream.seek(0)  # go to the beginning of the stream
        return send_file(
                excel_stream,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                attachment_filename="DRAFT-fire-ecology-traits-data-export-DRAFT.xlsx",
                as_attachment=True,
                cache_timeout=0
        )
    else:
        return render_template('data-export/download.html')
