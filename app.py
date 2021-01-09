from flask import Flask, render_template,url_for
from flask_sqlalchemy import SQLAlchemy
import csv
from numpy import genfromtxt


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
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
    return render_template('index.html',records=[records])#dictionaries can't be passed

if __name__ == "__main__":

    #Creating Database
    db.create_all()
    app.run(debug=True)
    
    
    


