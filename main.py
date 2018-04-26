from flask import Flask, request, redirect, render_template, session, flash
#from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy 
import cgi
from datetime import datetime
from sqlalchemy import desc

app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:abc3@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3BRST'
## conda install -c conda-forge flask-sqlalchemy
## conda install pymysql


class Blog(db.Model):
    
    id=db.Column(db.Integer,primary_key=True)    
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))
    pub_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
   
    def __init__(self, title,body,owner, pub_date=None):
        self.title = title
        self.body = body 
        if pub_date is None:
           pub_date = datetime.utcnow()
        self.pub_date = pub_date
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup','index','list_blogs']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
 
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        # Cond #1: User enters a username that is 
        # stored in the database with the correct password and is
        # redirected to the /newpost page with their username being stored in a session.
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        #Cond #3: User tries to login with a username that is not stored
        #in the database and is redirected to the /login page with a message that 
        #this username does not exist.
        elif not user:
            flash('No such user', 'error')
            return redirect('/login')
        #Cond #2: User enters a username that is 
        #stored in the database with an incorrect password and is redirected to the 
        #/login page with a message that their password is incorrect.
        elif not (user.password == password):
             flash('Incorrect password', 'error')
             return redirect('/login') 
    return render_template('login.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        username_error = '' 
        password_error = ''
        verify_error= ''

        ###########validate user's data###########################
        #  Cond #2:User leaves any of the username,
        #  password, or verify fields blank and gets an error message that
        #  one or more fields are invalid.
         # COND #5:User enters a password or username less than 3 characters long and 
        # gets either an invalid username or an invalid password message.
        
        if (len(username) < 3)  or (len(username) >20) or (len(username) ==0) or (not username.isalpha()):
            username=username
            username_error = 'Please enter your name - name length [3-20] - No space is allowed'
            flash("Please enter your name - name length [3-20] - No space is allowed",'error')
            
        # COND #5:User enters a password or username less than 3 characters long and 
        # gets either an invalid username or an invalid password message.
        if (len(password) < 3)  or (len(password) >20) or (len(password) ==0) or (not password.isalpha()):
            password_error = 'Please enter your password - password length [3-20] - No space is allowed'
            password=''
            flash('Please enter your password - password length [3-20] - No space is allowed','error')            
            #return redirect('/signup')
        
        # COND #4: User enters different strings into the password and verify fields and gets an 
        # error message that the passwords do not match.
        if not (password == verify):
            verify_error="Passwords do not match"
            verify=''
            flash('Passwords do not match','error')
            
           # return redirect('/signup')

        #COND 1:User enters new, valid username, a valid password, 
        # and verifies password correctly and is redirected to the
        #'/newpost' page with their username being stored in a session.
    
        if not username_error and not password_error and not verify_error :
            existing_user = User.query.filter_by(username=username).first()

            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
               
            else:
            # cond #3 User enters a username that already exists 
            # and gets an error message that username already exists.
                flash("User already exists",'error')
                return render_template('login.html')
            
        else:
            #template = jinja_env.get_template('index.html')
            return render_template('signup.html')
    
    return render_template('signup.html')



def get_current_bloglist(userid):  
    return Blog.query.filter_by(owner_id=userid).order_by(desc(Blog.pub_date)).all()

def get_all_blogs():
    #first get all blogs
    #for each blog object get the owner id and then the username for that blog to put in the tuple
    listBlogs=[]
    blogs = Blog.query.filter_by().order_by(desc(Blog.pub_date)).all()
    for blog in blogs:
        owner_id= blog.owner_id
        user = User.query.get(owner_id)
        username = user.username
        blogs_tuple =(blog,username)
        listBlogs.append(blogs_tuple)
    return listBlogs

@app.route('/add-blog', methods=['POST'])
def add_blog():
   
    title = request.form['title']
    body = request.form['body']
    title_error = '' 
    body_error = ''
    owner = User.query.filter_by(username=session['username']).first()
    
    if (len(title) ==0):
        title_error = 'Please write a blog title'
        body=body
    
    if (len(body) == 0):
        body_error = 'Please write a blog body'
        title=title
    
    if not title_error and not body_error:        
        new_blog = Blog(title,body,owner)
        db.session.add(new_blog)
        db.session.commit()        
        #return redirect('/blog')
        blog=Blog.query.filter_by(title=title).first()     
        blog_id=blog.id
        return redirect('/blog?id='+str(blog_id))
    else:
         return render_template('newpost.html',title=title,body=body,title_error=title_error,body_error=body_error)


@app.route('/newpost')
def new_post():
    return render_template('newpost.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

   
@app.route('/blog',methods=['GET'])
def list_blogs():
    
    blog_id = request.args.get('id')
    userid = request.args.get('userid')
    username =request.args.get('username')
   
    if(blog_id): 
        blog=Blog.query.get(blog_id)
        owner_id=blog.owner_id
        userObj = User.query.filter_by(id=owner_id).first()
        username = userObj.username  
        return render_template('blog.html',blog=blog,username=username)

        # Use case #3: is on the individual entry page (e.g., /blog?id=1) and
        #clicks on the author's username in the tagline and lands on
        #the individual blog user's page.
    elif(userid):
        blogs=get_current_bloglist(userid)
        userObj = User.query.filter_by(id=userid).first()
        username = userObj.username        
        return render_template('singleUser.html',blogs=blogs,username=username)

        # Use case# 2: is on the /blog page and clicks on
        #the author's username in the tagline and lands 
        #on the individual blog user's page.
    elif(username):
        userObj = User.query.filter_by(username=username).first()
        userid = userObj.id
        blogs=get_current_bloglist(userid)
        return render_template('singleUser.html',blogs=blogs,username=username)
    
    return render_template('blogs.html',listBlogs=get_all_blogs())

@app.route('/',methods=['GET'])
def index():
    
    # Use case #1:User is on the / page ("Home" page) 
    # and clicks on an author's username in the list and 
    # lands on the individual blog user's page.
    user_id = request.args.get('id')
    if(user_id):
       return redirect('/blog?userid='+str(user_id))
    else:
        users = User.query.all()
        return render_template('index.html',users=users)


if __name__ == "__main__":
    app.run()

#pip install Flask-SQLAlchemy
