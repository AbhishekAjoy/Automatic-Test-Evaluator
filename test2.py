from flask import Flask, render_template, url_for, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
import csv
from numpy import genfromtxt
from pathlib import Path
import question

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.secret_key = 'hUYF/khi+uGilH1'
db = SQLAlchemy(app)

class User(db.Model):
    user_id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    usertype = db.Column(db.Integer,nullable = False)

    def __init__(self,user_id,name,email,password,usertype):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.usertype = usertype
    


def WriteUserToDb(records):
    for record in records:
        user = User(record["user_id"],record["name"],record["email"],record["password"],record["usertype"])
        db.session.add(user)
        db.session.commit()

def DisplayUserFromDb():
    user = User.query.all()
    try:
        app.logger.info(type(user))
    except: 
        app.logger.info("select query Failed")
        
def initdb():
    with open("datasets/userdata.csv") as user_csv:
        data = csv.reader(user_csv, delimiter=',')
        first_line = True
        records=[]
        uid = 10000  
        for i in data:
            if not first_line:

                records.append({
                    "user_id":uid,
                    "name":i[0],
                    "email": i[1],
                    "password": i[2],
                    "usertype": i[3]
                })
            else:
                first_line = False
            uid = uid + 1
            
            
    WriteUserToDb(records)

@app.route('/',methods=['POST','GET'])   
def index():
    #Creating Database
    my_file = Path("main.db")
    if my_file.is_file():
        # file exists
        app.logger.info("db exists")
    else:
        app.logger.info("Initializing db...")
        db.create_all()
        initdb()
    #DisplayUserFromDb()#testing
    return redirect('/login')
    #return render_template('index.html',records=[records])#dictionaries can't be passed
    
@app.route('/login',methods=['POST','GET'])   
def login(): 
    session.pop('email', None)      #sign out if already signed in
    session.pop('name', None)
    session.pop('usertype', None)
    if request.method == "POST":
        
        if request.form.get("login"):
            email = request.form['email']
            password = request.form['password']
            if email == "":
                return render_template('login.html', error = "Enter a valid e-mail ID!")
            if password == "":
                return render_template('login.html', error = "Enter a password!")

            record = db.session.query(User.email, User.password, User.usertype, User.name).filter_by(email=email).first()
        
            if record is None:
                return render_template('login.html', error = "Account not found.")
            if record.password != password:
                return render_template('login.html', error = "Incorrect password.")
            else:
                session['email'] = email
                session['usertype'] = record.usertype
                session['name'] = record.name
                #return render_template('login.html', error = "Logged in!")
                return redirect('/dashboard')
        if request.form.get("signup"):
            return redirect('/signup')

    return render_template('login.html', error = " ")
    
@app.route('/createtest',methods=['POST','GET'])  
def create_test():
    if request.method == "POST":
        if request.form.get("cancel"):
            return redirect('/dashboard')
        if request.form.get("createtest"):
            test_name = request.form['testname']
            no_of_questions = request.form['qno']
            app.logger.info(type(no_of_questions))
            if test_name == "":
                return render_template('createtest.html', error = "Enter a valid test name!")
            if no_of_questions == "":
                return render_template('createtest.html', error = "Enter a valid no of questions!")
            question.index()()
            question_list = question.generateQuestions(no_of_questions)
            app.logger.info(question_list)
    return render_template('createtest.html')

@app.route('/signup',methods=['POST','GET'])   
def signup(): 
    if request.method == "POST":
        
        if request.form.get("back"):
            return redirect('/login')
            
        if request.form.get("signup"):
            email = request.form['email']
            name = request.form['name']
            password = request.form['password']
            if email == "":
                return render_template('register.html', error = "Enter a valid e-mail ID!")
            if name == "":
                return render_template('register.html', error = "Enter your name!")
            if password == "":
                return render_template('register.html', error = "Enter a password!")
            if request.form['usertype'] == 'student':
                usertype = 1
            else:
                usertype = 2

            record = db.session.query(User.email).filter_by(email=email).first()
        
            if record is None:
                uid = db.session.query(User.user_id).order_by(User.user_id.desc()).first().user_id + 1
                records=[]    
                records.append({
                    "user_id":uid,
                    "name":name,
                    "email": email,
                    "password": password,
                    "usertype": usertype
                    })
                WriteUserToDb(records)
   
                return render_template('login.html', error = "Account created.")
   
            else:
                return render_template('register.html', error = "An account associated with this e-mail ID already exists.")

    return render_template('register.html', error = " ")
    
@app.route('/dashboard',methods=['POST','GET'])   
def dashboard(): 
    if session['usertype'] == 1:
        return render_template('student_dash.html', username = session['name'])
    
    elif session['usertype'] == 2:
        return render_template('teacher_dash.html', username = session['name'])
  
if __name__ == "__main__":
    app.run(debug=True)