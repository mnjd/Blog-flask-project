from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import psycopg2
import os

POSTGRES = {
    'user': 'postgres',
    'pw': 'postgres1234',
    'db': 'blogflask',
    'host': 'localhost',
    'port': '5432',
}

app = Flask(__name__) # create the application instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES # load config from this file

#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

db = SQLAlchemy(app)


class Postblog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(20))
    text = db.Column(db.Text)
    created_at = db.Column(db.DateTime)


@app.route("/")
def list_articles():
    posts = Postblog.query.all()
    #created_at = post.created_at.strftime('%B %d, %Y at %H:%M:%S')
    return render_template('listarticles.html', posts=posts)

@app.route("/detailarticles/<int:pk>")
def detail_articles(pk):
    post = Postblog.query.filter_by(id=pk).one()
#    created_at = post.created_at.strftime('%B %d, %Y at %H:%M:%S')
    return render_template('detailarticles.html', post=post)

@app.route("/createarticle/")
def create_articles():
    return render_template('createarticle.html')

@app.route("/createpost/", methods=['POST'])
def create_post():
    title = request.form['title']
    subtitle = request.form['subtitle']
    author = request.form['author']
    text = request.form['text']
    #created_at = datetime.now().strftime('%B %d, %Y at %H:%M:%S')
    created_at = datetime.now().strftime('%B %d, %Y at %H:%M:%S')

    post = Postblog(title=title, subtitle=subtitle, author=author, text=text, created_at=created_at)

    db.session.add(post)
    db.session.commit()
    return redirect(url_for('list_articles'))

@app.route("/editpost/<int:id>", methods=['GET', 'POST'])
def edit_post(id):
    post = db.session.query(Postblog).filter(Postblog.id==id).first()
    
    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        author = request.form['author']
        text = request.form['text']
        
        post.title = title
        post.subtitle = subtitle
        post.author = author
        post.text = text

        db.session.commit()

        return redirect(url_for('list_articles'))
    elif request.method == 'GET':
        return render_template('editarticle.html', post=post)

@app.route("/deletepost/<int:id>", methods=['POST'])
def delete_post(id):
    post = db.session.query(Postblog).filter(Postblog.id==id).first()
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('list_articles'))

if __name__ == "__main__":
    app.run(debug=True)
