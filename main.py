from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(280))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

blog_id = ""

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'bloglist', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        if not username or not password or not verify:
            flash('Make sure to fill out all fields', 'error')
            return render_template('signup.html')
        if len(username) < 3:
            flash('Make a username that is 3 characters or longer', 'error')
            return render_template('signup.html')
        if len(password) < 3:
            flash('Make a password that is 3 characters or longer', 'error')
            return render_template('signup.html')
        if not password == verify:
            flash('Make sure both passwords match')
            return render_template('signup.html')
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists')
            return render_template('signup.html')
        if not existing_user and password == verify:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('Invalid Username', 'error')
            return render_template('login.html')
        if user and not user.password == password:
            flash("Invalid Password", 'error')
        if user and user.password == password:
            session['username'] = username
            flash("Logged In")
            return redirect('/newpost')
    return render_template('login.html')

@app.route('/newpost', methods=['POST','GET'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        username = session['username']
        owner = User.query.filter_by(username=username).first()

        if not title:
            flash('Please enter something as a title', 'error')
            return render_template('newpost.html', body=body)
        elif not body:
            flash('Please enter something as a post', 'error')
            return render_template('newpost.html', title=title)

        else:
            new_blog = Blog(title, body, owner)
            db.session.add(new_blog)
            db.session.commit()
            blog_id = str(new_blog.id)
            return redirect('/blog?id=' + blog_id)
    return render_template('newpost.html')

@app.route('/blog', methods=['POST','GET'])
def bloglist():
    blog = request.args.get('id', default=None, type=int)
    user = request.args.get('user', default=None, type=int)
    if user:
        blogs = Blog.query.filter_by(owner_id=user)
        return render_template('singleUser.html', blogs=blogs)
    if blog is None:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)
    else:
        blog_id = Blog.query.filter_by(id=blog).first()
        return render_template('viewblog.html', blog_id=blog_id)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run()