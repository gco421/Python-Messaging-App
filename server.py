# import Flask
from flask import Flask, render_template, redirect, request, session, flash
#import mySQL
from mysqlconnection import connectToMySQL
# the "re" module will let us perform some regular expression operations
import re
# create a regular expression object that we can use run operations on
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)     # we are creating an object called bcrypt, 
                         # which is made by invoking the function Bcrypt with our app as an argument
app.secret_key = "b'\x17R\x81\x9a\xc4\xbcg\x9a\xbc\xc2K\xad\xd5\xb6\xec\r'"

@app.route("/")
def index():
    if 'loggedin' not in session:
        session['loggedin']=False
    else:
        session['loggedin']=True
    return render_template("index.html")

@app.route("/regprocess", methods=['POST'])
def register():
    # Add validation rules
    #validation for first name
    if len(request.form['f_n']) == 0:
        flash("First name cannot be blank!", 'f_n')
    elif len(request.form['f_n']) <= 2:
        flash("First name must be 2+ characters", 'f_n')

    #validation for last name
    if len(request.form['l_n']) == 0:
        flash("Last name cannot be blank!", 'l_n')
    elif len(request.form['l_n']) <= 2:
        flash("Last name must be 2+ characters", 'l_n')

    #validation for email
    if len(request.form['email']) == 0:
        flash("Email cannot be blank!", 'email')
    elif not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address!", 'email')
    mysql = connectToMySQL("wall")
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data = { "email" : request.form["email"] }
    result = mysql.query_db(query, data)
    if result:
        flash("The email already exists")

    #validation for password    
    if len(request.form['password']) == 0:
        flash("Password cannot be blank!", 'email')
    elif len(request.form['password']) < 8:
        flash("Password needs to be at least 8 characters!", 'email')
    if request.form['password_confirmation'] != request.form['password']:
        flash("Passwords don't match!", 'email')
    if '_flashes' in session.keys():
        # pass form data to sessions so that user doesn't need to reinput correct input. they would just edit the incorrect input.
        session['f_n'], session['l_n'], session['email']= request.form['f_n'], request.form['l_n'], request.form['email']
        return redirect("/")

    else:
    # include some logic to validate user input before adding them to the database!
    # create the hash
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        mysql = connectToMySQL("wall")
        data = {
            'f_n':request.form['f_n'],
            'l_n':request.form['l_n'],
            'email':request.form['email'],
            'password_hash':pw_hash
        }
        query= "INSERT INTO users(f_n, l_n, email, password, created_at, updated_at) VALUES(%(f_n)s,%(l_n)s,%(email)s,%(password_hash)s,NOW(),NOW());"
        session['user_id'] = mysql.query_db(query, data)
        return redirect('/regsuccess')
    return redirect('/')

@app.route("/regsuccess")
def success():
    return render_template("regsuccess.html")

@app.route('/loginprocess', methods=["POST"])
def login():
    # extra security measure in case hacker makes the post a get. this checks if there is a POST request
    if request.method != 'POST':
        session.clear()
        return redirect('/')

    # see if the email provided exists in the database
    mysql = connectToMySQL("wall")
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data = { "email" : request.form["email"].strip().lower() } #extra measures to strip email of blank spaces which is a default function if nothing to strip is specified and also makes the email lowercase
    result = mysql.query_db(query, data)
    if result:
        # assuming we only have one user with this username, the user would be first in the list we get back
        # of course, we should have some logic to prevent duplicates of usernames when we create users
        # use bcrypt's check_password_hash method, passing the hash from our database and the password from the form
        if bcrypt.check_password_hash(result[0]['password'], request.form['password']):
            # if we get True after checking the password, we may put the user id in session
            session['user_id'] = result[0]['id']
            session['f_n'] = result[0]['f_n']
            session['l_n'] = result[0]['l_n']
            # never render on a post, always redirect!
            return redirect('/loggedin')
    # if we didn't find anything in the database by searching by username or if the passwords don't match,
    # flash an error message and redirect back to a safe route
    flash("You could not be logged in")
    return redirect("/")

@app.route("/loggedin")
def loggedin():
    if 'user_id' not in session:
        return redirect('/')

    mysql = connectToMySQL("wall")
    #get user info from db
    data = {'id': session['user_id']}
    #This is a self join!
    #Message query
    query = """SELECT users.f_n AS f_n, 
            users2.f_n AS sender_fn,
            users2.l_n AS sender_ln,
            messages.id AS message_id, 
            messages.message AS message, 
            messages.user_id AS sender_id, 
            DATE_FORMAT(messages.created_at,GET_FORMAT(DATE, 'USA')) AS created_at 
            FROM users 
            JOIN messages ON messages.user_id = users.id 
            JOIN users AS users2 ON users2.id = messages.user_id
            ORDER BY created_at desc;"""
    messagedata= mysql.query_db(query,data)

    #comments
    mysql = connectToMySQL("wall")
    data = {'id': session['user_id']}
    query = """SELECT 
        users.f_n AS sender_fn,
        users.l_n AS sender_ln,
        comments.id AS comment_id, 
        comments.comment AS comment, 
        comments.user_id AS sender_id, 
        DATE_FORMAT(comments.created_at,GET_FORMAT(DATE, 'USA')) AS created_at 
        FROM users 
        JOIN comments ON comments.user_id = users.id 
        JOIN users AS users2 ON users2.id = comments.user_id
        JOIN messages ON messages.id = comments.message_id
        WHERE comments.message_id = messages.id;"""
    commentdata= mysql.query_db(query,data)

    # print(messagedata)

    #getting user first names from the database
    mysql = connectToMySQL('wall')
    query = 'SELECT f_n FROM users WHERE id = %(id)s;'
    data = {'id': session['user_id']}
    user = mysql.query_db(query, data)

    #getting user info from the database
    mysql = connectToMySQL('wall')
    query = 'SELECT * FROM users WHERE id = %(id)s;'
    data = {'id': session['user_id']}
    user = mysql.query_db(query, data)

    # Get the user list without the logged in user
    mysql = connectToMySQL('wall')
    query = 'SELECT id AS receiver_id, f_n AS receiver_name FROM users WHERE id != %(id)s;'
    otherusers = mysql.query_db(query, data)
    # save the users data from the mysql query so it can be used in jinja in html file

    # print("*"*20,"Debugging","*"*20)
    
    return render_template("loggedin.html", messagedata=messagedata,commentdata=commentdata) 
   

@app.route("/sendmsg", methods=["POST"])
def sendmsg():
    data={
        "message": request.form['message'],
        "user_id": session['user_id'],
    }
    mysql = connectToMySQL("wall")
    query = "INSERT into messages(message,created_at, updated_at, user_id) VALUES (%(message)s,NOW(), NOW(),%(user_id)s);"
    mysql.query_db(query, data)
    # print("*"*20,"Debugging1","*"*20)
    # print(request.form)
    return redirect("/loggedin")
    
@app.route('/delete/<id>')
def delete(id):
    if 'user_id' not in session:
        session.clear()
        return redirect('/')
    # delete messages
    data = {'id': id}
    mysql = connectToMySQL('wall')
    query = 'DELETE FROM messages WHERE id = %(id)s'
    mysql.query_db(query, data)

    #then delete comments
    data = {'id': id}
    mysql = connectToMySQL('wall')
    query = 'DELETE FROM comments WHERE id = %(id)s'
    mysql.query_db(query, data)
    
    return redirect('/loggedin')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/comment', methods=["POST"])
def comment():
    data={
    "comment": request.form['comment'],
    "user_id": session['user_id'],
    "message_id": request.form['message_id']
    }
    mysql = connectToMySQL('wall')
    query = "INSERT into comments(comment,created_at, updated_at, user_id, message_id) VALUES (%(comment)s,NOW(), NOW(),%(user_id)s, %(message_id)s);"
    mysql.query_db(query, data)
    # print("*"*20,"Debugging1","*"*20)
    # print(request.form)
    return redirect("/loggedin")

if __name__=="__main__":
    app.run(debug=True) 