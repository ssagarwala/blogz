from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import cgi
from datetime import datetime
from sqlalchemy import desc

app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:MyNewPass2@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))
    pub_date = db.Column(db.DateTime)
   
    def __init__(self, title,body,pub_date=None):
        self.title = title
        self.body = body 
        if pub_date is None:
           pub_date = datetime.utcnow()
        self.pub_date = pub_date


def get_current_bloglist():
    return Blog.query.order_by(desc(Blog.pub_date)).all()

@app.route('/add-blog', methods=['POST'])
def add_blog():
   
    title = request.form['title']
    body = request.form['body']
    title_error = '' 
    body_error = ''
    
    if (len(title) ==0):
        title_error = 'Please write a blog title'
        body=body
    
    if (len(body) == 0):
        body_error = 'Please write a blog body'
        title=title
    
    if not title_error and not body_error:        
        new_blog = Blog(title,body)
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

   
@app.route('/blog',methods=['GET'])
def index():
    
    blog_id = request.args.get('id')
   
    if(blog_id): 
        blog=Blog.query.get(blog_id)
        return render_template('blog.html',blog=blog)
    else: 
        return render_template('blogs.html',blogs=get_current_bloglist())

if __name__ == "__main__":
    app.run()
