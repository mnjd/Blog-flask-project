from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import psycopg2

POSTGRES = {
    'user': 'postgres',
    'pw': 'postgres1234',
    'db': 'blogflask',
    'host': 'localhost',
    'port': '5432',
}

app = Flask(__name__) # create the application instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES # load config from this file

db = SQLAlchemy(app)

class postblog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(20))
    text = db.Column(db.Text)
    created_at = db.Column(db.DateTime)

@app.route("/")
def list_articles():
    return render_template('listarticles.html')

@app.route("/detailarticles/")
def detail_articles():
    return render_template('detailarticles.html')

@app.route("/createarticle/")
def createarticle():
    return render_template('createarticle.html')

if __name__ == "__main__":
    app.run(debug=True)
