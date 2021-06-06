from flask import Flask, render_template, url_for, redirect, request, session
from flask import send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import csv
import pandas as pd
from numpy import genfromtxt
from pathlib import Path
import datetime
import evaluator
from numpy import genfromtxt
import random
import string


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SQLALCHEMY_BINDS'] = {'question':'sqlite:///question.db','response':'sqlite:///response.db','test':'sqlite:///test.db'}
app.secret_key = 'hUYF/khi+uGilH1'
db = SQLAlchemy(app)



class Test(db.Model):
    __bind_key__ = 'test'
    test_id = db.Column(db.Integer,primary_key = True)
    test_name = db.Column(db.String(100), nullable=False)
    creator_id = db.Column(db.Integer)
    question_list = db.Column(db.String(200), nullable=False)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    def __init__(self,test_id,test_name,creator_id,question_list,start_time,end_time):
        self.test_id = test_id
        self.test_name = test_name
        self.creator_id = creator_id
        self.question_list = question_list

        self.start_time = start_time
        self.end_time = end_time


def WriteTestToDb(records):
    for record in records:
        test = Test(record["test_id"],record["test_name"],record["creator_id"],record["question_list"],record["start_time"],record["end_time"])
        db.session.add(test)
        db.session.commit()





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



""" def DisplayUserFromDb():
    user = User.query.all()
    try:
        app.logger.info(type(user))
    except: 
        app.logger.info("select query Failed")

 """

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

class Response(db.Model):
    __bind_key__ = 'response'
    __table_args__ = (
        db.PrimaryKeyConstraint('test_id', 'student_id','question'),
    )
    
    test_id = db.Column(db.Integer)
    student_id = db.Column(db.Integer)
    question = db.Column(db.String(200), nullable=False)
    answer = db.Column(db.String(200), nullable=False)
    pointsAwarded = db.Column(db.Integer)

    def __init__(self, test_id, student_id, question, answer, pointsAwarded):
        self.test_id = test_id
        self.student_id = student_id
        self.question = question
        self.answer = answer
        self.pointsAwarded = pointsAwarded

def WriteResponseToDb(records):
    for record in records:
        response = Response(record["test_id"],record["student_id"],record["question_id"],record["answer"], record["score"])
        db.session.add(response)
        db.session.commit()
            

class Question(db.Model):
    __bind_key__ = 'question'
    question_id = db.Column(db.Integer,primary_key = True)
    questionTitle = db.Column(db.String(200), nullable=False)
    referenceAnswer = db.Column(db.String(1000), nullable=False)
    questionType = db.Column(db.Integer, nullable=False) #0 is MCQ, 1 is fill blanks,2 is match,3 descriptive
    options = db.Column(db.String(200))# Used for mcq and match
    marks = db.Column(db.Integer)

    def __init__(self, question_id,questionTitle,referenceAnswer,questionType,options,marks):
        self.question_id = question_id
        self.questionTitle = questionTitle
        self.referenceAnswer = referenceAnswer
        self.questionType = questionType
        self.options = options
        self.marks = marks



def WriteQToDb(records):
    for record in records:
        question = Question(record["question_id"],record["questionTitle"],record["referenceAnswer"],record["questionType"],record["options"],record["marks"])
        db.session.add(question)
        db.session.commit()



def ExtractQFromDb(question_list):
    questions = []
    for q in question_list:
        questions.append(Question.query.filter_by(question_id = q).first())
    try:
        return questions
    except: 
        app.logger.info("ExtractQFromDb(): question extraction from db Failed")



def evaluatemarks(questionanswer):
    return evaluator.evaluate(questionanswer)



def generateQuestions(no_of_questions):
    q = Question.query.all()
    question_list = []
    question_list = random.sample(range(1001,1001+len(q)), no_of_questions)
    return question_list



def initQdb():
    with open("datasets/DatasetFinalcsv.csv") as user_csv:
        data = csv.reader(user_csv, delimiter=',')
        first_line = True
        records=[]
        qid = 1000
        for i in data:
            if not first_line:
                qid = qid + 1
                records.append({
                    "question_id":qid,
                    "questionTitle":i[0],
                    "referenceAnswer": i[1],
                    "questionType": int(i[2]),
                    "options":(None if i[3] in (None, "") else i[3]),#only present for mcq and match
                    "marks": (5 if int(i[2])>=2 else 1)#5 for mcq and match, 1 for others, changable afterwards
                })
            else:
                first_line = False
        
    WriteQToDb(records)



@app.route('/student_response',methods=['POST','GET']) 
def student_response():
    score = 0
    max_score = 0
    dcount = 0
    mcqcount = 0
    fillcount = 0
    result = []
    scores = []
    answers= []
    refans = []
    qtype = []
    matchops = []
    option = []
    try:
        #Getting form data from question.html
        selected_question = request.form.getlist('selectedquestion')
        descanswer = request.form.getlist('descanswer')
        #The option here is the option selected by the student
        
        
        fillanswer = request.form.getlist("fillanswer")
        result.append(selected_question)
        for i in range(0,len(selected_question)):
            q = Question.query.filter_by(questionTitle = selected_question[i]).first()
            refans.append(q.referenceAnswer)
            qtype.append(q.questionType)

            record = {}
            record['test_id'] = session['test_id']
            record['student_id'] = session['user_id']
            record['question_id'] = q.question_id

            score = 0
            if q.questionType == 0:#MCQ
                opid = "option" + str(q.question_id)
                option.append(request.form.get(opid))
                ans = option[mcqcount]
                if option[mcqcount] == q.referenceAnswer:
                    score = score + q.marks
                max_score = max_score + q.marks
                scores.append(score)

                mcqcount = mcqcount + 1
                record['score'] = score

            elif q.questionType == 1:#Fill in the blanks
                ans = fillanswer[fillcount]
                ref = q.referenceAnswer
                if fillanswer[fillcount].lower() == ref.lower():
                    score = score + q.marks
                max_score = max_score + q.marks
                scores.append(score)

                fillcount = fillcount + 1
                record['score'] = score

            elif q.questionType == 2:#Match the following
                m = []
                mid = "matchans" + str(q.question_id)
                matchans = request.form.getlist(mid)
                matchops.append(q.options)
                for i in q.referenceAnswer:
                    if i != ',':
                        m.append(i)
                l = len(m)
                ans = ','.join(matchans)
                for i in range(0,l):
                    if matchans[i] == m[i]:
                        score = score + q.marks/l
                max_score = max_score + q.marks
                scores.append(score)
                record['score'] = score
            else:#Descriptive
                
                response = []
                ans = descanswer[dcount]
                response.append(ans)
                response.append(q.questionTitle)
                response.append(q.referenceAnswer)

                try:
                    if ans != '':
                        markObtained = round(evaluatemarks(response)*q.marks,0) #executes function in evaluator.py and returns marks
                    else:
                        markObtained = 0
                    score = score + markObtained
                    max_score = max_score + q.marks
                    dcount = dcount + 1
                except Exception as e:
                    app.logger.info(e)
                    app.logger.info("descriptive answer evaluation error")
                scores.append(score)
                record['score'] = score

            answers.append(ans)
            record['answer'] = ans
            if session['usertype']==1:
                try:
                    WriteResponseToDb([record])
                except Exception as e:
                    app.logger.info(e)
    except:
        app.logger.info("Failed to submit data")
    return redirect('/dashboard')



@app.route('/',methods=['POST','GET'])   
def index():
    #Question Database
    my_file_question = Path("question.db")
    if my_file_question.is_file():
        # file exists
        app.logger.info("question db exists")
    else:
        app.logger.info("Initializing question db...")
        db.create_all(bind = 'question')
        initQdb()


    #Test Database
    my_file_test = Path("test.db")
    if my_file_test.is_file():
        # file exists
        app.logger.info("test db exists")
    else:
        app.logger.info("Initializing test db...")
        db.create_all(bind='test') 


    #Response Database
    my_file_question = Path("response.db")
    if my_file_question.is_file():
        # file exists
        app.logger.info("response db exists")
    else:
        app.logger.info("Initializing response db...")
        db.create_all(bind = 'response')


    #Creating User Database
    my_file_user = Path("main.db")
    if my_file_user.is_file():
        # file exists
        app.logger.info("user db exists")
    else:
        app.logger.info("Initializing user db...")
        
         #creates db,initializes values
        db.create_all()
        initdb()
    #DisplayUserFromDb()#testing
    return redirect('/login')
    


@app.route('/login',methods=['POST','GET'])   
def login(): 
    session.pop('email', None)      #sign out if already signed in
    session.pop('name', None)
    session.pop('usertype', None)
    session.pop('test_id', None)
    session.pop('user_id', None)
    if request.method == "POST":
        
        if request.form.get("login"):
            email = request.form['email']
            password = request.form['password']
            if email == "":
                return render_template('login.html', error = "Enter a valid e-mail ID!")
            if password == "":
                return render_template('login.html', error = "Enter a password!")

            record = db.session.query(User.email, User.password, User.usertype, User.name, User.user_id).filter_by(email=email).first()
        
            if record is None:
                return render_template('login.html', error = "Account not found.")
            if record.password != password:
                return render_template('login.html', error = "Incorrect password.")
            else:
                session['email'] = email
                session['usertype'] = record.usertype
                session['name'] = record.name
                session['user_id'] = record.user_id
                #return render_template('login.html', error = "Logged in!")
                return redirect('/dashboard')
        """ if request.form.get("signup"):
            return redirect('/signup') """

    return render_template('login.html', error = " ")


@app.route('/deletequestiondb',methods=['POST','GET'])
def deletequestiondb():
    response = []
    response.append(session['name'])
    if request.method == "POST":
        questionname = request.form.get("delquestionname")
        try:
            q = Question.query.filter(func.lower(Question.questionTitle) == func.lower(questionname)).first()
            if q is not None:
                Question.query.filter_by(questionTitle = q.questionTitle).delete()
                return render_template('teacher_dash.html', info = [response], error = "Question successfully deleted")
            else:
                return render_template('teacher_dash.html', info = [response], error = "Could not find Question")
            
        except Exception as e:
                return render_template('teacher_dash.html', info = [response], error = e)
@app.route('/addquestiondb',methods=['POST','GET'])
def addquestiondb():
    if request.method == "POST":
        qtype = -1
        matchno = -1
        mcqno = 0
        opstr = ""
        if request.form.get("add"):
            x = request.form.get("qtype")
            if x:
                qtype = int(x)
                return render_template('addquestiondb.html',gottype = int(x))

        """ ________________MCQ_______________"""
        
        if request.form.get("mcqadd"):
            qtype = 0

            if request.form.get("mcqopno"):
                y = request.form.get("mcqopno")
                mcqq = request.form.get("mcqq")
                if y:
                    mcqno = int(y)
                    if mcqno > 0:
                        return render_template('addquestiondb.html',gottype = qtype, opno = mcqno,q = mcqq)
                    else:
                         return render_template('addquestiondb.html',error ="Enter a valid no of options")
        if request.form.get("mcqadd2"):
            qtype = 0
            mcqno = int(request.form.get("mno"))
            mcqq = request.form.get("mcqqt")
            opstr = request.form.get("1")
            for i in range(2,mcqno+1):
                opstr = opstr + ',' + request.form.get(str(i))
            mcqans = request.form.get(request.form.get("mcqans")) 

            if mcqq == "":
                return render_template('addquestiondb.html', error = "Enter a valid question")
            if mcqans == "":
                return render_template('addquestiondb.html', error = "Enter a valid answer") 
            record = db.session.query(Question.questionTitle).filter_by(questionTitle=mcqq).first() 
            if record is None:
                qid = db.session.query(Question.question_id).order_by(Question.question_id.desc()).first().question_id + 1
                records=[]    
                
                records.append({
                    "question_id":qid,
                    "questionTitle":mcqq,
                    "referenceAnswer": mcqans,
                    "questionType": qtype,
                    "options":opstr,#only present for mcq and match
                    "marks": 1
                    })
                WriteQToDb(records)
                q = db.session.query(Question.questionTitle).filter_by(questionTitle=mcqq).first()
                if q is None:
                    app.logger.info("Question saving failed")
                    return render_template('addquestiondb.html', error = "Question saving failed")
                else:
                    app.logger.info("Question: " + q.questionTitle + " Saved succesfully")
                    return redirect('/dashboard')
            else:
                return render_template('addquestiondb.html', error = "Question already exists")
        
        """ ________________Fill in the blanks_______________"""

        if request.form.get("filq"):
            qtype = 1
            fillq = request.form.get("filq")
            fillans = request.form.get("filans")
            if fillq == "":
                return render_template('addquestiondb.html', error = "Enter a valid question")
            if fillans == "":
                return render_template('addquestiondb.html', error = "Enter a valid answer")
            
            record = db.session.query(Question.questionTitle).filter_by(questionTitle=fillq).first()
            if record is None:
                qid = db.session.query(Question.question_id).order_by(Question.question_id.desc()).first().question_id + 1
                records=[]    
                
                records.append({
                    "question_id":qid,
                    "questionTitle":fillq,
                    "referenceAnswer": fillans,
                    "questionType": qtype,
                    "options":None,#only present for mcq and match
                    "marks": 1
                    })
                WriteQToDb(records)
                q = db.session.query(Question.questionTitle).filter_by(questionTitle=fillq).first()
                if q is None:
                    app.logger.info("Question saving failed")
                    return render_template('addquestiondb.html', error = "Question saving failed")
                else:
                    app.logger.info("Question: " + q.questionTitle + " Saved succesfully")
                    return redirect('/dashboard')
            else:
                return render_template('addquestiondb.html', error = "Question already exists")

        """ ________________Descriptive Answer_______________"""

        if request.form.get("descq"):
            qtype = 3
            descq = request.form.get("descq")
            descans = request.form.get("descans")
            if descq == "":
                return render_template('addquestiondb.html', error = "Enter a valid question")
            if descans == "":
                return render_template('addquestiondb.html', error = "Enter a valid answer")
            
            record = db.session.query(Question.questionTitle).filter_by(questionTitle=descq).first()
            if record is None:
                qid = db.session.query(Question.question_id).order_by(Question.question_id.desc()).first().question_id + 1
                records=[]    
                
                records.append({
                    "question_id":qid,
                    "questionTitle":descq,
                    "referenceAnswer": descans,
                    "questionType": qtype,
                    "options":None,#only present for mcq and match
                    "marks": 5
                    })
                WriteQToDb(records)
                q = db.session.query(Question.questionTitle).filter_by(questionTitle=descq).first()
                if q is None:
                    app.logger.info("Question saving failed")
                    return render_template('addquestiondb.html', error = "Question saving failed")
                else:
                    app.logger.info("Question: " + q.questionTitle + " Saved succesfully")
                    return redirect('/dashboard')
            else:
                return render_template('addquestiondb.html', error = "Question already exists")   

        """ ________________Match the following_______________""" 

        if request.form.get("matchsub1"):
            qtype = 2
            matchno = int(request.form.get("matchno"))
            if matchno <= 1:
                return render_template('addquestiondb.html',error ="Enter a valid no of options")
            else:
                return render_template('addquestiondb.html',gottype = qtype,matchnum = matchno)

        if request.form.get("matchsub2"):
            qtype = 2
            z = request.form.get("matno")
            matno = int(z)
            matchcorrect = []
            matchleft = []
            matchright = []
            for i in range(0,matno):
                matchleft.append(request.form.get("mleft" + str(i)))
                matchright.append(request.form.get("mright" + str(i)))
                matchcorrect.append(request.form.get("mcorrect" + str(i)))
                if matchleft[i] == '' or matchcorrect[i] == '' or matchright[i] == '':
                    return render_template('addquestiondb.html',gottype = qtype,matchnum = matno,error = "Enter a valid input for match")
            qTitle = ",".join(matchleft)
            qoptions = ",".join(matchright)
            qref = ",".join(matchcorrect)

            record = db.session.query(Question.questionTitle).filter_by(questionTitle=qTitle).first()
            if record is None:
                qid = db.session.query(Question.question_id).order_by(Question.question_id.desc()).first().question_id + 1
                records=[]    
                
                records.append({
                    "question_id":qid,
                    "questionTitle":qTitle,
                    "referenceAnswer": qref,
                    "questionType": qtype,
                    "options":qoptions,#only present for mcq and match
                    "marks": matno
                    })
                WriteQToDb(records)
                q = db.session.query(Question.questionTitle).filter_by(questionTitle=qTitle).first()
                if q is None:
                    app.logger.info("Question saving failed")
                    return render_template('addquestiondb.html', error = "Question saving failed")
                else:
                    app.logger.info("Question: " + q.questionTitle + " Saved succesfully")
                    return redirect('/dashboard')
            
    return render_template('addquestiondb.html')



@app.route('/createtest',methods=['POST','GET'])  
def create_test():
    question_list = []
    if request.method == "POST":
        if request.form.get("cancel"):
            return redirect('/dashboard')
        if request.form.get("createtest"):
            test_name = request.form['testname']
            no_of_questions = request.form['qno']
            date = request.form.get("date")
            start = request.form.get("start")
            end = request.form.get("end")
            fstart = start.split(":")
            app.logger.info(fstart)
            fend = end.split(":")
            fdate = date.split("-")
            app.logger.info(fdate)
            try:
                starttime = datetime.datetime(int(fdate[0]),int(fdate[1]),int(fdate[2]),int(fstart[0]),int(fstart[1]))
            except:
                return render_template('createtest.html', error = "Please enter correct start time in HH:MM format")
            
            try:
                endtime = datetime.datetime(int(fdate[0]),int(fdate[1]),int(fdate[2]),int(fend[0]),int(fend[1]))
            except:
                return render_template('createtest.html', error = "Please enter correct end time in HH:MM format")
            if test_name == "":
                return render_template('createtest.html', error = "Enter a valid test name!")
            if no_of_questions == "":
                return render_template('createtest.html', error = "Enter a valid no of questions!")
            if request.form.get("randomize"):
                question_list = generateQuestions(int(no_of_questions))
            elif request.form.get("select"):
                q = Question.query.all()
                return render_template('createtest.html',qno = no_of_questions, questions = q, testname = test_name,s = start,e = end ,d = date)
        if request.form.get("createtest2"):
            no_of_questions  = int(request.form.get("qno"))
            start = request.form.get("st")
            end = request.form.get("et")
            date = request.form.get("dt")
            start = start.split(':')
            end = end.split(":")
            date = date.split("-")
            app.logger.info(date)
            try:
                starttime = datetime.datetime(int(date[0]),int(date[1]),int(date[2]),int(start[0]),int(start[1]))
            except:
                return render_template('createtest.html', error = "2Please enter correct start time in HH:MM format")
            
            try:
                endtime = datetime.datetime(int(date[0]),int(date[1]),int(date[2]),int(end[0]),int(end[1]))
            except:
                return render_template('createtest.html', error = "Please enter correct end time in HH:MM format")
            test_name = request.form.get("tname")
            for i in range(0,no_of_questions):
                question_list.append(int(request.form.get("question" + str(i))))
           
        string_ints = [str(i) for i in question_list]
        qlist = ",".join(string_ints)
        x = Test.query.all()
        if not x:
            testid = 1
        else:
            testid = db.session.query(Test.test_id).order_by(Test.test_id.desc()).first().test_id + 1
        u = User.query.filter_by(email = session['email']).first()
        records=[]    
        records.append({
            "test_id":testid,
            "test_name":test_name,
            "creator_id": u.user_id,
            "question_list": qlist,
            "start_time": starttime,
            "end_time" : endtime
            })  
        WriteTestToDb(records)
        return redirect('/dashboard')
            

    return render_template('createtest.html')



@app.route('/viewtest',methods=['POST','GET'])   
def viewtest(): 
    if request.method == "POST":
        if request.form.get('view'):
            session['test_id'] = request.form.get('view')
            test = Test.query.filter_by(test_id = session['test_id'])
            x = test[0].question_list
            end = test[0].end_time
            start = test[0].start_time
            question_list = map(int, x.split(','))
            questions = ExtractQFromDb(question_list)
            return render_template('question.html',questions = [questions],endTime = end,startTime = start,utype = session['usertype'])
            
        elif request.form.get('delete'):
            y = request.form.get('delete')
            Test.query.filter_by(test_id=y).delete()
            Response.query.filter_by(test_id=y).delete()
            db.session.commit()
            return redirect('/dashboard')
            
        elif request.form.get('results'):
            session['test_id'] = request.form.get('results')
            return redirect('/results')
            
def get_answers(student_id):
    questions = []
    result = []
    scores = []
    answers= []
    refans = []
    qtype = []
    matchops = []
    maxscore = 0
    
    responses = Response.query.filter_by(student_id = student_id).filter_by(test_id = session['test_id'])
    for response in responses:
        question = Question.query.filter_by(question_id = response.question).first()
        questions.append(question.questionTitle)
        refans.append(question.referenceAnswer)
        answers.append(response.answer)
        qtype.append(question.questionType)
        if question.questionType == 2:
            matchops.append(question.options)
        scores.append(response.pointsAwarded)
        maxscore = maxscore + question.marks
      
    result.append(questions)              
    result.append(refans)
    result.append(answers)
    result.append(qtype)
    result.append(matchops)
    result.append(scores)
    result.append(maxscore)#maxscore
    return result
    
@app.route('/view_answers',methods=['POST','GET'])   
def view_answers():
    if session['usertype']==1:
        student_id = session['user_id']
        session['test_id'] = request.form.get('results')
        return render_template('display.html',response = [get_answers(student_id)])
    else:
        if request.method == "POST":
            if request.form.get('view'):
                student_id = request.form.get('view')
                return render_template('display.html',edit = student_id,response = [get_answers(student_id)])
            if request.form.get("changescore"):
                q = request.form.get("question")
                question = Question.query.filter_by(questionTitle = q).first()
                qid = question.question_id
                student_id = request.form.get("stud_id")
                student_id = int(student_id)
                index = request.form.get("index")
                scorechange = "scorechange" + index
                try:
                    response = Response.query.filter_by(question = qid,student_id = student_id,test_id = session['test_id']).first()
                    marks = request.form.get(scorechange)
                    response.pointsAwarded = int(marks)
                    db.session.commit()
                    return render_template('display.html',edit = student_id,response = [get_answers(student_id)])
                except Exception as e:
                    return render_template('display.html',error = e, edit = student_id,response = [get_answers(student_id)])
                
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
        response = []
        response.append(session['name'])
        completedTests = Response.query.filter_by(student_id = session['user_id'])
        tests = Test.query.filter_by()
        for test in tests:
            testComplete = False
            for completedTest in completedTests:
                if completedTest.test_id == test.test_id:
                    testComplete = True
                    break
            if testComplete == False:
                currentTime = datetime.datetime.utcnow()+datetime.timedelta(hours=5.5)
                if currentTime >= test.start_time and currentTime <= test.end_time:
                    response.append({"test_id":test.test_id,
                        "test_name":test.test_name,
                        "creator_id": test.creator_id,
                        "question_list": test.question_list
                        })

        return render_template('student_dash.html', info = [response])
        
    elif session['usertype'] == 2:
        response = []
        response.append(session['name'])
        u = User.query.filter_by(email = session['email']).first()
        tests = Test.query.filter_by(creator_id = u.user_id)
        for test in tests:
            response.append({"test_id":test.test_id,
                "test_name":test.test_name,
                "creator_id": test.creator_id,
                "question_list": test.question_list
                })

        return render_template('teacher_dash.html', info = [response])
    elif session['usertype'] == 3:
        response = []
        response.append(session['name'])
        return render_template('admin_dash.html', info = [response])
        
@app.route('/results',methods=['POST','GET'])   
def results(): 
    if session['usertype'] == 1:
        response = []
        response.append(session['name'])
        completedTests = Response.query.filter_by(student_id = session['user_id'])
        tests = Test.query.filter_by()
        for test in tests:
            testComplete = False
            for completedTest in completedTests:
                if completedTest.test_id == test.test_id:
                    testComplete = True
                    break
            if testComplete == True:
                currentTime = datetime.datetime.utcnow()+datetime.timedelta(hours=5.5)
                if currentTime >=test.end_time:
                    response.append({"test_id":test.test_id,
                        "test_name":test.test_name,
                        "creator_id": test.creator_id,
                        "question_list": test.question_list
                        })

        return render_template('student_dash_results.html', info = [response])
     
    elif session['usertype'] == 2:
        data = []
        testname = Test.query.filter_by(test_id = session['test_id']).first().test_name
        results = db.session.query(Response.student_id, db.func.sum(Response.pointsAwarded).label('score')).group_by(Response.student_id).order_by(db.desc(db.func.sum(Response.pointsAwarded))).filter_by(test_id = session['test_id']).all()
        for result in results:
            student_name = db.session.query(User.name).filter(User.user_id==result.student_id).first().name
            data.append({"student_id":result.student_id,
                "student_name":student_name,
                "score":result.score,
                })
        return render_template('results.html', testname = testname, table = data)



@app.route('/download-user-csv',methods=['POST','GET'])   
def downloadfile():
    return send_file('datasets/adduser.csv',
                     mimetype='text/csv',
                     attachment_filename='adduser.csv',
                     as_attachment=True)



@app.route('/upload-user-csv',methods=['POST','GET'])   
def uploadfile():
    response = []
    response.append(session['name'])
    if request.method == 'POST':
        files = request.files['file']
        try:
            data = pd.read_csv(files)
        except:
            return render_template('admin_dash.html',error = "Please click browse to upload file",info = [response]) 
        records = []
        uid = db.session.query(User.user_id).order_by(User.user_id.desc()).first().user_id
        try:
            for i in range(0,len(data.name)):
                u = User.query.filter_by(email = data.email[i]).first()
                if u is None:
                    uid = uid + 1
                    records.append({
                                "user_id":uid,
                                "name":data.name[i],
                                "email": data.email[i],
                                "password": data.password[i],
                                "usertype": int(data.usertype[i])
                                })
            if not records:
                return render_template('admin_dash.html',error = "No users were added",info = [response])                    
            WriteUserToDb(records)
            return render_template('admin_dash.html',error = "User successfully added",info = [response])
        except :
            return render_template('admin_dash.html',error = "Error in format of Uploaded File",info = [response])


@app.route('/delete-user',methods=['POST','GET'])   
def deleteUser():
    response = []
    response.append(session['name'])
    if request.method == "POST":
        delemail = request.form.get("delemail")
        u = User.query.filter_by(email = delemail).first()
        if u is not None:
            uid = User.query.filter_by(email = delemail).first().user_id
            Response.query.filter_by(student_id=uid).delete()
            User.query.filter_by(email=delemail).delete()
            db.session.commit()
            return render_template('admin_dash.html',error = "User successfully deleted",info = [response]) 
        else:
            return render_template('admin_dash.html',error = "email not found",info = [response]) 
if __name__ == "__main__":
    app.run(debug=True)