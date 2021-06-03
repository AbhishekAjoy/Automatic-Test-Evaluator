from flask import Flask, render_template,url_for,request
from flask_sqlalchemy import SQLAlchemy
import csv
import evaluator
from numpy import genfromtxt
from pathlib import Path
import random


question = Flask(__name__)
question.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///question.db'
db = SQLAlchemy(question)
class Question(db.Model):
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

def ExtractFromDb(question_list):
    questions = []
    for q in question_list:
        questions.append(Question.query.filter_by(question_id = q).first())
    try:
        return questions
    except: 
        question.logger.info("ExtractFromDb(): question extraction from db Failed")

def evaluatemarks(questionanswer):
    return evaluator.evaluate(questionanswer)

def generateQuestions(no_of_questions):
    q = Question.query.all()
    question_list = []
    for i in range(0,no_of_questions):
        n = random.randint(1001,1001+len(q) - 1)
        if n in question_list:
            i = i - 1
            continue
        else:
            question_list.append(n)
    return question_list

def initdb():
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

@question.route('/student_response',methods=['POST','GET']) 
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
    try:
        #Getting form data from question.html
        selected_question = request.form.getlist('selectedquestion')
        descanswer = request.form.getlist('descanswer')
        #The option here is the option selected by the student
        option = request.form.getlist("option")
        matchans = request.form.getlist("matchans")
        fillanswer = request.form.getlist("fillanswer")
        result.append(selected_question)
        for i in range(0,len(selected_question)):
            q = Question.query.filter_by(questionTitle = selected_question[i]).first()
            refans.append(q.referenceAnswer)
            qtype.append(q.questionType)
            score = 0
            if q.questionType == 0:#MCQ
                ans = option[mcqcount]
                if option[mcqcount] == q.referenceAnswer:
                    score = score + q.marks
                max_score = max_score + q.marks
                scores.append(score)
                question.logger.info(option[mcqcount])
                question.logger.info(score)
                mcqcount = mcqcount + 1
            elif q.questionType == 1:#Fill in the blanks
                ans = fillanswer[fillcount]
                if fillanswer[fillcount] == q.referenceAnswer:
                    score = score + q.marks
                max_score = max_score + q.marks
                scores.append(score)
                question.logger.info(fillanswer[fillcount])
                question.logger.info(score)
                fillcount = fillcount + 1
            elif q.questionType == 2:#Match the following
                m = []
                matchops.append(q.options)
                for i in q.referenceAnswer:
                    if i != ',':
                        m.append(i)
                l = len(m)
                ans = matchans
                for i in range(0,l):
                    if matchans[i] == m[i]:
                        score = score + q.marks/l
                max_score = max_score + q.marks
                scores.append(score)
                question.logger.info(m)
                question.logger.info(score)

            else:#Descriptive
                
                response = []
                ans = descanswer[dcount]
                response.append(ans)
                response.append(q.questionTitle)
                response.append(q.referenceAnswer)
                question.logger.info(response)
                try:
                    markObtained = round(evaluatemarks(response)*q.marks,0) #executes function in evaluator.py and returns marks
                    score = score + markObtained
                    max_score = max_score + q.marks
                    dcount = dcount + 1
                except:
                    question.logger.info("descriptive answer evaluation error")
                scores.append(score)
                question.logger.info(score)
            answers.append(ans)
    except:
        question.logger.info("Failed to submit data")
    result.append(refans)
    result.append(answers)
    result.append(qtype)
    result.append(matchops)
    result.append(scores)
    result.append(max_score)
    question.logger.info(result)
    return render_template('display.html',response = [result])#Page after answer submission

@question.route('/',methods=['POST','GET'])   
def index():
#The commented code should be only executed to initialize the database
    my_file = Path("question.db")
    if my_file.is_file():
        # file exists
        question.logger.info("db exists")
    else:
        question.logger.info("Initializing db...")
        db.create_all()
        initdb() #creates db,initializes values

    #Below code for generating random list of question ids
    #Use generateQuestions()
    """ q = Question.query.all()
    question_list = []
    no_of_questions = 5
    for i in range(0,no_of_questions):
        n = random.randint(1001,1001+len(q) - 1)
        if n in question_list:
            i = i - 1
            continue
        else:
            question_list.append(n)
 """
    question_list = [1007,1036,1037,1021,1038]
    questions = ExtractFromDb(question_list)
    #question.logger.info(question_list)
    return render_template('question.html',questions = [questions])#dictionaries can't be passed, during init change questions var to records= [records]
if __name__ == "__main__":
    question.run(debug=True)
    
    