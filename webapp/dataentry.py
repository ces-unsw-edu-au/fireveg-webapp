from flask import (
    Blueprint, flash, g, redirect, render_template, current_app, request, url_for, send_file
)
import pandas as pd
import io

from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db
from webapp.xlfile import create_input_xl
from webapp.pg import get_pg_connection
from psycopg2.extras import DictCursor
import openpyxl


bp = Blueprint('dataentry', __name__, url_prefix='/data-entry')

@bp.route('/', methods=('GET', 'POST'))
@login_required
def howto():
    if request.method == 'POST':
        # Quick option, for small instances
        return send_file(current_app.config['DATAENTRY'],         attachment_filename="fire-ecology-traits-data-entry-form.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            cache_timeout=0
        )
    else:
        return render_template('data-entry.html', the_title="Data Entry")

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
        # Quick option, for small instances
        return send_file(current_app.config['DATAENTRY'],         attachment_filename="fire-ecology-traits-data-entry-form.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            cache_timeout=0
        )
        # If we can afford a better instance, we can use this time/resource consumming alternative:

        #contactinfo = request.form
        #wb = openpyxl.load_workbook(current_app.config['DATAENTRY'])
        #if contactinfo is not None:
        #     ws = wb['Contributor']
        #     ws.cell(row=2,column=2,value=contactinfo['Name'])
        #     ws.cell(row=3,column=2,value=contactinfo['Affiliation'])
        #     ws.cell(row=4,column=2,value=contactinfo['Contact'])
        #
        # excel_stream = io.BytesIO()
        # wb.save(excel_stream)
        # excel_stream.seek(0)  # go to the beginning of the stream
        # return send_file(
        #         excel_stream,
        #         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        #         attachment_filename="fire-ecology-traits-data-entry-form.xlsx",
        #         as_attachment=True,
        #         cache_timeout=0)
    else:
        return render_template('data-entry/download.html')
