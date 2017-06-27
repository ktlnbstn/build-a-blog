from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True

# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:moopoo@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y247kGhns&zP3B'

class BlogPost(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    completed = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, owner):
        self.title = title
        self.body = body
        self.completed = False
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    posts = db.relationship('BlogPost', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash('Logged In')
            return redirect('/')
        else:
            flash('User password incorrect or user does not exist', 'error')

    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        #TODO validate user's data

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            #TODO user better response messaging
            return '<h1>Duplicate user</h1>'

    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

@app.route('/', methods=['POST', 'GET'])
def index():

    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        blog_name = request.form['blog']
        new_post = BlogPost(blog_name, owner)
        db.session.add(new_post)
        db.session.commit()

    posts = BlogPost.query.filter_by(completed=False, owner=owner).all()
    completed_posts = BlogPost.query.filter_by(completed=True, owner=owner).all()
    return render_template('blog_post.html', title="Blog Name Here!", posts=posts,
        completed_posts=completed_posts)

@app.route('/delete-post', methods=['POST'])
def delete_post():
    post_id = int(request.form['post-id'])
    post = BlogPost.query.get(post_id)
    blog.completed = True
    db.session.add(post)
    db.session.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run()
