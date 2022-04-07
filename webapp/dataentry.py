from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import pandas as pd

from werkzeug.exceptions import abort

from webapp.auth import login_required
from webapp.db import get_db

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
