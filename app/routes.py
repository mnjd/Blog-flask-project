from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from urllib.parse import urlparse, urljoin
from datetime import datetime
import redis

POSTGRES = {
    'user': 'postgres',
    'pw': '',
    'db': 'blogflask',
    'host': 'localhost',
    'port': '5434',
}

app = Flask(__name__)  # create the application instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:%(pw)s@%(host)\
                                        s:%(port)s/%(db)s' % POSTGRES
app.config['SECRET_KEY'] = 'thisissecret'
app.config['USE_SESSION_FOR_NEXT'] = True

db = SQLAlchemy(app)
ma = Marshmallow(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Postblog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(20))
    text = db.Column(db.Text)
    created_at = db.Column(db.DateTime)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Weatherdb(db.Model):
    dateandtime = db.Column(db.DateTime, primary_key=True)
    city = db.Column(db.String(50))
    temperature = db.Column(db.Integer)
    humidity = db.Column(db.Integer)
    pressure = db.Column(db.Integer)
    temperature_ressentie = db.Column(db.Integer)
    description = db.Column(db.String(50))


class PostListAPIView(ma.Schema):
    class Meta:
        fields = ('id',
                  'title',
                  'subtitle',
                  'author',
                  'text',
                  'created_at'
                  )


@app.route('/api/v1.0/posts/', methods=['GET'])
def get_posts():
    postlist = PostListAPIView(many=True)
    queryset = Postblog.query.all()
    posts = postlist.dump(queryset)
    return jsonify(posts.data)


@app.route("/")
def list_articles():
    posts = Postblog.query.all()
    r = redis.StrictRedis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)
    temperature = r.get('temperature')
    city = r.get('city')
    apparent_temperature = r.get('apparent_temp')
    description = r.get('description')
    return render_template('listarticles.html', posts=posts, temperature=temperature, city=city, apparent_temperature=apparent_temperature, description=description)

@app.route('/login')
def login():
    session['next'] = request.args.get('next')
    return render_template('login.html')

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
            ref_url.netloc == test_url.netloc

@app.route('/logmein', methods=['POST'])
def logmein():
    username = request.form['username']

    user = User.query.filter_by(username=username).first()

    if not user:
        return '<h1> User not found</h1>'

    login_user(user)

    if 'next' in session:
        next = session['next']
        if is_safe_url(next):
            return redirect(next)

    return '<h1>You are logged in!</h1>'

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return 'You are now logged out!'

@app.route("/detailarticles/<int:pk>")
def detail_articles(pk):
    post = Postblog.query.filter_by(id=pk).one()
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
    created_at = datetime.now().strftime('%B %d, %Y at %H:%M:%S')

    post = Postblog(title=title,
                    subtitle=subtitle,
                    author=author,
                    text=text,
                    created_at=created_at
                    )

    db.session.add(post)
    db.session.commit()
    return redirect(url_for('list_articles'))


@app.route("/editpost/<int:id>", methods=['GET', 'POST'])
def edit_post(id):
    post = db.session.query(Postblog).filter(Postblog.id == id).first()

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
    post = db.session.query(Postblog).filter(Postblog.id == id).first()
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('list_articles'))


if __name__ == "__main__":
    app.run(debug=True)
