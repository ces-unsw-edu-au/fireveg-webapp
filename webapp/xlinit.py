## This script is for creating workbooks and saving them in the instance folder of the deployment
# These functions are intended to be triggered by admin user on a regular basis, for example by calling a cron job


import click
from flask import current_app, g
from flask.cli import with_appcontext

import pandas as pd
from webapp.xlfile import create_input_xl, create_output_xl, create_list_records_xl
from webapp.pg import get_pg_connection
from psycopg2.extras import DictCursor

# https://stackoverflow.com/questions/63329657/python-3-7-error-unsupported-pickle-protocol-5
#import pickle5 as pickle

import pickle

## First, load SQL queries

with open('webapp/content/sql_queries.pik', 'rb') as f:
 qryCategorical, qryNumeric, qryRefs, qryTraits, qryAllRefs, qrySomeTraits, qrySpps, qryVocabs, qryMethodVocabs, qryCat, qryNum, qryCatMet, qryNumMet = pickle.load(f)

## Load other content from pickle:

with open('webapp/content/common_data.pik', 'rb') as f:
    general_supporters,general_info = pickle.load(f)

with open('webapp/content/data_entry_data.pik', 'rb') as f:
    input_wsheets, input_instructions, input_links = pickle.load(f)

with open('webapp/content/output_summary_data.pik', 'rb') as f:
    output_wsheets, output_description = pickle.load(f)

## Next, declare functions to be used for summarising values in the workbook cells

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

## Now, define command line commands
# These functions are intended to be triggered by admin user on a regular basis, for example by calling a cron job


@click.command('init-recordlist-export')
@with_appcontext
def init_recordexport_command():
    pg = get_pg_connection()
    cur = pg.cursor(cursor_factory=DictCursor)

    cur.execute(qryTraits)
    trait_info = cur.fetchall()

    traitnames=dict()
    for k in trait_info:
        traitnames[k[0]]={'name':k[1],'type':k[3],'method':k["method_vocabulary"] is not None}

    records=list()
    traits = ['surv1','surv4','repr2','rect2','disp1','germ1','germ8','repr3','repr3a','repr4',]
    colnames = ['scientific name','current code (BioNET)','original name','CAPS code',
                'trait code','trait name','norm value','method','weight','source ref','other ref','recordid']
    for trait in traits:
        if traitnames[trait]['type']=='categorical' and traitnames[trait]['method']==False:
            cur.execute(qryCat.format(trait=trait,traitname=traitnames[trait]['name']))
        elif traitnames[trait]['type']=='categorical' and traitnames[trait]['method']==True:
            cur.execute(qryCatMet.format(trait=trait,traitname=traitnames[trait]['name']))
        elif traitnames[trait]['type']=='numeric' and traitnames[trait]['method']==True:
            cur.execute(qryNumMet.format(trait=trait,traitname=traitnames[trait]['name']))
        else:
            cur.execute(qryNum.format(trait=trait,traitname=traitnames[trait]['name']))
        res = cur.fetchall()
        records.extend(res)

    df = pd.DataFrame(records,columns=colnames)

    flat_list=df['source ref'].unique().tolist()
    for sublist in df['other ref'].tolist():
        if sublist is not None:
            flat_list.extend(sublist)

    valid_refs=tuple(set(flat_list))

    cur.execute(qryRefs,(valid_refs,))
    ref_info = cur.fetchall()


    cur.close()

    wb = create_list_records_xl(traitsummary=df, referencelist=ref_info, traitlist=trait_info, info=general_info, wsheets=output_wsheets, description=output_description, supporters=general_supporters)
    wb.save(current_app.config['RECORDXPORT'])
    click.echo('Template saved at designated location')


@click.command('init-data-export')
@with_appcontext
def init_dataexport_command():
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
    cur.execute(qryRefs,(valid_refs,))
    ref_info = cur.fetchall()


    cur.execute(qryTraits)
    trait_info = cur.fetchall()

    cur.close()

    wb = create_output_xl(traitsummary=df, referencelist=ref_info, traitlist=trait_info, info=general_info, wsheets=output_wsheets, description=output_description, supporters=general_supporters)
    wb.save(current_app.config['DATAXPORT'])
    click.echo('Template saved at designated location')



@click.command('init-dataentry')
@with_appcontext
def init_dataentryform_command():
    pg = get_pg_connection()
    cur = pg.cursor(cursor_factory=DictCursor)

    cur.execute(qrySpps)
    spps = cur.fetchall()

    cur.execute(qryAllRefs)
    refs = cur.fetchall()

    cur.execute(qrySomeTraits)
    traits = cur.fetchall()

    cur.execute(qryVocabs)
    vocabs = cur.fetchall()

    cur.execute(qryMethodVocabs)
    mvocabs = cur.fetchall()

    cur.close()

    wb = create_input_xl(contactinfo=None, referencelist=refs, specieslist=spps, traitlist=traits, vocabularies=vocabs, methods_vocabularies=mvocabs,
    wsheets=input_wsheets, instructions=input_instructions, links=input_links)

    wb.save(current_app.config['DATAENTRY'])
    click.echo('Template saved at designated location')

## Now, register these commands in the init_app function

def init_app(app):
    app.cli.add_command(init_dataentryform_command)
    app.cli.add_command(init_dataexport_command)
    app.cli.add_command(init_recordexport_command)
