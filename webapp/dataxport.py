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
    if request.method == 'POST':

        return send_file(current_app.config['DATAXPORT'],         attachment_filename="DRAFT-fire-ecology-traits-data-export-DRAFT.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            cache_timeout=0
        )
    else:
        return render_template('data-export/download.html')
