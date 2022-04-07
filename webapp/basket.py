from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db
from webapp.pg import get_pg_connection

from psycopg2.extras import DictCursor
import pandas as pd

bp = Blueprint('basket', __name__, url_prefix='/report')

@bp.route('/fam_list')
@login_required
def fam_list():
    if 'spcodes' in session:
        spps = session.get('spcodes')

    if len(spps)>0:
        pg = get_pg_connection()
        cur = pg.cursor()

        cur.execute(
        """
        SELECT family AS fam,"scientificName","speciesID" FROM species.caps WHERE "speciesID" IN %s ORDER BY fam;
        """,(tuple(spps),)
        )
        fam_list = cur.fetchall()
        cur.close()
        return render_template('basket/fam-list.html', records=fam_list, the_title="Species per family")
    else:
        return session
        #redirect(url_for('species.fam_list'))

@bp.route('/add/spcode/', methods = ['GET', 'POST'])
@login_required
def addspcode():
    if 'spcodes' in session:
        spplist = session.get('spcodes')
    else:
        spplist=list()
    if 'spnames' in session:
        sppnames = session.get('spnames')
    else:
        sppnames=list()

    if request.method == 'POST':
        requested_names = request.form['spplist'].split(",")
        for sppname in requested_names:
            sppname = sppname.strip(" ")
            if sppname.isnumeric():
                if sppname not in spplist:
                    spplist.append(sppname)
            else:
                if sppname not in sppnames:
                    sppnames.append(sppname)
        msg = "The request included %s names or codes, there are now %s species codes and %s species names in the selection." % (len(requested_names),len(spplist),len(sppnames))
    elif request.method == 'GET':
        newspp = request.args.get('spcode')
        if newspp not in spplist:
            spplist.append(newspp)
        msg = "Species with code %s was succesfully added, there are now %s species codes in the list" % (newspp,len(spplist))
    session['spcodes']=spplist
    session['spnames']=sppnames
    #return session
    #return redirect(url_for('basket.fam_list'))
    return render_template('basket/query-form.html', inherited_message=msg)
