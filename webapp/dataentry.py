from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_file
)
import pandas as pd
import io

from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db
from webapp.xlfile import create_input_xl
from webapp.pg import get_pg_connection
from psycopg2.extras import DictCursor

bp = Blueprint('dataentry', __name__, url_prefix='/data-entry')


@bp.route('/upload', methods=('GET', 'POST'))
@login_required
def upload_file():
    if request.method == 'POST':
        print(request.files['file'])
        f = request.files['file']
        data_xls = pd.read_excel(f)
        return data_xls.to_html()
    return render_template('data-entry/upload.html')

## create and download excel file for data entry:

@bp.route('/download', methods=('GET', 'POST'))
@login_required
def download_file():
    if request.method == 'POST':
        response = request.form

        pg = get_pg_connection()
        cur = pg.cursor(cursor_factory=DictCursor)
        cur.execute('SELECT "scientificName","speciesCode_Synonym" FROM species.caps;')
        spps = cur.fetchall()

        cur.execute("SELECT ref_code,ref_cite FROM litrev.ref_list")
        refs = cur.fetchall()

        cur.execute("SELECT code,name,description,value_type,life_stage,life_history_process,priority FROM litrev.trait_info WHERE priority IS NOT NULL ORDER BY code ")
        traits = cur.fetchall()

        cur.execute("""
SELECT code, category_vocabulary, method_vocabulary,
pg_catalog.obj_description(t.oid, 'pg_type')::json as vocab
FROM litrev.trait_info i
LEFT JOIN pg_type t
    ON t.typname=i.category_vocabulary
WHERE category_vocabulary IS NOT NULL
ORDER BY code""")
        vocabs = cur.fetchall()

        cur.close()

        wb = create_input_xl(contactinfo=response, referencelist=refs, specieslist=spps, traitlist=traits, vocabularies=vocabs)
        excel_stream = io.BytesIO()
        wb.save(excel_stream)
        excel_stream.seek(0)  # go to the beginning of the stream
        return send_file(
                excel_stream,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                attachment_filename="File.xlsx",
                as_attachment=True,
                cache_timeout=0
        )
    else:
        return render_template('data-entry/download.html')
