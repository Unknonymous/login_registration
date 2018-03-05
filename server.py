from flask import Flask, render_template, session, request, flash, redirect
 
#import the connector function  !!!ensure that the msqlconnection.py file is in the server's root directory
from mysqlconnection import MySQLConnector

#assign app to Flask 
app = Flask(__name__)

#use md5 to hash PW
import md5

#import the regex module
import re
#SAMPLE_REGEX = re.compile(r'^ ... $')
#build REGEX list

#letters only, 2+ characters
NAME_REGEX = re.compile(r'^[a-zA-Z]{2,}$')

#valid email format (copy this from lesson material)
EMAIL_REGEX = re.compile(r'^[a-zA_Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

# 8+ characters
PASS_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]{8,}$')

#pass DB name to the function
mysql = MySQLConnector(app, 'login_reg')     
#assign secret key if session will be used, else comment this line
app.secret_key = 'FFFlask2020'                         
 
#sample query to test the db connection
# print mysql.query_db('SELECT * FROM ... ')


 
@app.route('/', methods=['POST','GET'])
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    #set vars for posted data
    fname = request.form['fname']
    lname = request.form['lname']
    email = request.form['email']
    passw = request.form['passw']
    cpass = request.form['cpass']

    #validate posted data
    errors = 0
    #fname must be alpha & 2+ chars
    if not NAME_REGEX.match(fname) or len(fname) < 2:
        errors += 1
        flash ('First name is required:  2+ characters, alpha only.')

    #lname must be alpha & 2+ chars
    if not NAME_REGEX.match(lname) or len(lname) < 2:
        errors += 1
        flash ('Last name is required: 2+ characters, alpha only.')

    #email must be present & formatted
    if not EMAIL_REGEX.match(email) or len(email) < 2:
        errors += 1
        flash ('Email address is required: format = example@address.com')
    
    #password must be proper length & match confirmation
    if passw != cpass:
        errors += 1
        flash ('Password and Password Confirmation must match.')
    elif not PASS_REGEX.match(passw):
        errors += 1
        flash ('Password is required: at least 8 characters.')
    
    #show erros on index
    if errors > 0:
        return redirect ('/')
    else:
        #proceed with db entry and login
        #hash password
        hpass = md5.new(passw).hexdigest()

        #build data dictionary for insert query
        data = {
            'fname' : fname,
            'lname' : lname,
            'email' : email,
            'hpass' : hpass,
        }
        query = "INSERT INTO users (first_name, last_name, email_address, password, created_at, updated_at ) VALUES (:fname, :lname, :email, :hpass, NOW(), NOW() )" 

        #execute insertion & get id for login
        session['id'] = mysql.query_db(query, data)

        # gotID = mysql.query_db("SELECT LAST_INSERT_ID()")
        # session['id'] = gotID[0]['gotID']
        
        return redirect('/success')

@app.route('/logging',methods=['POST'])
def logging():
    
    errors = 0

    #collect email & pw from form
    email = request.form['logmail']
    passw = request.form['logpass']

    #email must be present & formatted
    if not EMAIL_REGEX.match(email) or len(email) < 2:
        errors += 1
        flash ('Email address is required: format = example@address.com')

    #password must be present & proper length
    if not PASS_REGEX.match(passw):
        errors += 1
        flash ('Password is required: at least 8 characters.')

    #if errors return to login/registration & flash error msg
    if errors > 0:
        return redirect('/')
    else:   #retrieve user data & validate password
        
        data = {
            'email' : email
        }

        query = "SELECT password FROM users WHERE email_address = :email LIMIT 1"
        queryReturn = mysql.query_db(query, data)
        storedHash = queryReturn[0]['password']
        
        newHash = md5.new(passw).hexdigest()

        if newHash == storedHash:
            #get login data
            inData = {
                "password" : newHash,
                "email_address" : email
            }
            inQuery = "SELECT id FROM users WHERE email_address = :email_address AND password = :password LIMIT 1"
            session['id'] = mysql.query_db(inQuery, inData)[0]['id']

            return redirect('/success')
        else: #flash login fail message & return to login page
            flash ('Incorrect username or password')
            return redirect('/')



@app.route('/success',methods=['GET'])
def success():

    #build query for login confirmation
    logId = session['id']
    data = {
        'logId' : logId
    }
    query = "SELECT CONCAT(first_name,' ',last_name) AS 'name', email_address AS 'email' FROM users WHERE id = :logId"
    loginfo = mysql.query_db(query, data)
    
    return render_template('success.html', logInfo = loginfo)



app.run(debug=True)