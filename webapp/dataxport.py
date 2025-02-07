from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_file, send_from_directory, current_app
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


## create and download excel file for data export:

@bp.route('/download', methods=('GET', 'POST'))
@login_required
def download_file():
    s3list=[
        'https://fireveg-db.s3.ap-southeast-2.amazonaws.com/output-report/fireveg-trait-records-model.xlsx',
        'https://fireveg-db.s3.ap-southeast-2.amazonaws.com/output-report/fireveg-field-report-model.xlsx'
    ]
    role = g.user.role
    print("role")
    print("role")
    print(role)
    return render_template('data-export/download.html',s3file=s3list, role=role)
