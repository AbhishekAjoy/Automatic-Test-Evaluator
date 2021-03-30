from flask import Flask, render_template, url_for, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
import csv
from numpy import genfromtxt


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.secret_key = 'hUYF/khi+uGilH1'
db = SQLAlchemy(app)
currentUser = ""

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
        

@app.route('/',methods=['POST','GET'])   
def index():
    
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
    DisplayUserFromDb()#testing
    #return redirect('/login')#
    return render_template('index.html',records=[records])#dictionaries can't be passed
    
@app.route('/login',methods=['POST','GET'])   
def login(): 
    session.pop('email', None)      #sign out if already signed in
    session.pop('usertype', None)
    if request.method == "POST":
        
        if request.form.get("login"):
            email = request.form['email']
            password = request.form['password']
            if email == "":
                return render_template('login.html', error = "Enter a valid e-mail ID!")
            if password == "":
                return render_template('login.html', error = "Enter a password!")

            record = db.session.query(User.email, User.password, User.usertype).filter_by(email=email).first()
        
            if record is None:
                return render_template('login.html', error = "Account not found.")
            if record.password != password:
                return render_template('login.html', error = "Incorrect password.")
            else:
                session['email'] = email
                session['usertype'] = record.usertype
                return render_template('login.html', error = "Logged in!")
                
        if request.form.get("signup"):
            return redirect('/signup')

    return render_template('login.html', error = " ")
    
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
    
if __name__ == "__main__":

    #Creating Database
    db.create_all()
    app.run(debug=True)
 

    
    
    


