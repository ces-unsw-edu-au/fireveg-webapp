from flask import Flask, render_template
import psycopg2
from configparser import ConfigParser
from pathlib import Path

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

application = app
repodir = Path("./")

def get_db_connection():
    filename = repodir / 'secrets' / 'database.ini'
    section = 'aws-lght-sl'
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    conn = psycopg2.connect(**db)
    return conn

# first route
@app.route('/')
def index():
    return render_template('index.html', the_title="Home / index")

# other routes
@app.route('/about')
def about():
    return render_template('about.html', the_title="Home / About")

# sites

@app.route('/list/sites')
def sites():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT site_label,location_description FROM form.field_site ORDER BY site_label;')
    site_list = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('site-list.html', pairs=site_list, the_title="Field Work locations")

@app.route('/site/<id>')
def detail(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT site_label,location_description,elevation,st_x(geom),st_y(geom),st_srid(geom) FROM form.field_site WHERE site_label='%s';" % id)
    try:
        site_info = cur.fetchone()
    except:
        return f"<h1>Invalid site label: {id}</h1>"
    cur.close()
    conn.close()
    return render_template('site-info.html', info=site_info, the_title=id)


#@app.route('/dashboard')
#@login_required
#def account():
#    return render_template("account.html")

# keep this as is
if __name__ == '__main__':
    app.run(debug=True)
