from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(280))

    def __init__(self, title, body):
        self.title = title
        self.body = body

blog_id = ""

@app.route('/newpost', methods=['POST','GET'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if not title:
            flash('Please enter something as a title', 'error')
            return render_template('newpost.html', body=body)
        elif not body:
            flash('Please enter something as a post', 'error')
            return render_template('newpost.html', title=title)

        else:
            new_blog = Blog(title, body)
            db.session.add(new_blog)
            db.session.commit()
            blog_id = str(new_blog.id)
            return redirect('/blog?id=' + blog_id)
    return render_template('newpost.html')

@app.route('/blog', methods=['POST','GET'])
def bloglist():
    blog = request.args.get('id', default=None, type=int)
    if blog is None:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)
    else:
        blog_id = Blog.query.filter_by(id=blog).first()
        return render_template('viewblog.html', blog_id=blog_id)
@app.route('/')
def send_to_blog():
    return redirect('/blog')

if __name__ == '__main__':
    app.run()