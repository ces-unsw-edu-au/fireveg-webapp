# Fireveg webapp based on Python/flask

## Documentation

This version has been developed following steps in
https://flask.palletsprojects.com/en/2.0.x/tutorial/

and now we are using flask `3.0.2`
### Set up

Create a virtual environment for flask with miniconda:

```sh
conda create --name flsk
conda activate flsk
```

or with venv... in our local machine

```sh
python3 -m venv ~/proyectos/flsk
source ~/proyectos/flsk/bin/activate
## or source ~/proyectos/venv/flsk/bin/activate

```
or with venv... in our local machine(Windows)

```sh
cd /path to the root folder of your directory
python -m venv .venv
.venv\Scripts\activate

```

or with venv... in the cloud instance within the project/fireveg-webapp folder:

```sh
source venv/bin/activate
```

Check python version
```sh
python --version
```

Update and install modules
```sh
pip install --upgrade pip
#/usr/local/opt/python@3.9/bin/python3.9 -m pip install --upgrade pip
pip3 install -U Flask
pip install psycopg2-binary
pip install flask-wtf
pip install folium
pip install pandas
pip install datetime
pip install openpyxl
pip install SQLAlchemy
pip install Flask-SQLAlchemy
pip install Flask-Migrate
pip install Flask-Cors
pip install python-dotenv
pip install sendgrid
pip install PyJWT
```

Create and initialise directory
```sh
mkdir -p ~/proyectos/fireveg/fireveg-webapp
cd ~/proyectos/fireveg/fireveg-webapp
git init
```

```sh
pip freeze > requirements.txt
```

### Setup the env file
Navigate to your project directory in Command Prompt and create a new file `.env`
```sh
DATABASE_URI=<your_database_uri_here>
JWT_SECRET_KEY=<your_jwt_secret_key_here>
SENDGRID_API_KEY=<your_sendgrid_api_key_here>
```
Replace <your_database_uri_here>, <your_jwt_secret_key_here> and <your_sendgrid_api_key_here> with your actual Database connection, JWT secret key and SendGrid API key, respectively.

### Setup the database migrations
Initialize the database migration,To create a new migration To apply the migrations and update your database schema, these commands will setup your PostgresQL Database.
```sh
flask db init
flask db migrate -m "fist migration"

flask db upgrade
```

### Test the app on ubuntu

```sh
# conda activate flsk ## or
# source ~/proyectos/venv/flsk/bin/activate
cd ~/proyectos/fireveg/fireveg-webapp
export FLASK_APP=webapp
export FLASK_DEBUG=TRUE
# initialise test admin user
flask create_test_admin
# run the webapp
flask run
```

### Test the app on windows
```sh
Navigate to your project directory in Command Prompt
.venv\Scripts\activate
set FLASK_APP=webapp
set FLASK_DEBUG=1
# initialise sqlite database if doesn't exists
#[ -e instance/webapp.sqlite ] || flask init-db
# run the webapp
flask run
```

### Database credentials

A `database.ini` file must be added to the `instance` folder to be able to connect to the postgresql database with the information for the database host, port, database name, user and password.

```sh
[aws-lght-sl]
host=...
port=...
database=...
user=...
password=...
```


### Update the data entry form

First update the pickle files with content for the data entry form:
```sh
cd ~/proyectos/fireveg-webapp/webapp

python xlcontent.py
```

Create a folder for the upload of files:
```sh
cd ~/proyectos/fireveg/fireveg-webapp/ ## or
cd ~/proyectos/fireveg-webapp/

mkdir -p instance/uploaded_files/litrev
mkdir -p instance/uploaded_files/fieldform
```

For the field work proforma, we just copy the file provided by David, since we have not replicated this form in our python scripts:

```sh
mv ~/Desktop/FireResponseProforma_20220621\[1\].docx ~/proyectos/fireveg/fireveg-webapp/instance/field-work-proforma.xlsx

```

For the other data entry and export forms, we can use the app functions below:

```sh
cd ~/proyectos/fireveg/fireveg-webapp ## or
cd ~/proyectos/fireveg-webapp/
export FLASK_APP=webapp
export FLASK_DEBUG=TRUE
# export FLASK_ENV=development # deprecated
flask init-dataentry
flask init-data-export
flask init-recordlist-export
```

### Updating/upgrading Python

There are some difference with function `send_file` between Flask version 2.0.2 and 2.2.2 will need to test different virtual environments to see if it is worth upgrading in the deployment or downgrading in the local machine.



### Running with gunicorn

```sh
pip install gunicorn
cd ~/proyectos/fireveg/fireveg-webapp
gunicorn -w 4 --reload --bind 0.0.0.0:5000 "webapp:create_app()"
```

### Other on-line resources

https://python-adv-web-apps.readthedocs.io/en/latest/flask.html

https://www.digitalocean.com/community/tutorials/how-to-use-a-postgresql-database-in-a-flask-application
