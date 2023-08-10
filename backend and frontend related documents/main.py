from flask import Flask, render_template, request,session,redirect  ,jsonify
import psycopg2
from flask_session import Session
from json import dumps
from datetime import date
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.static_folder='static'
Session(app)
conn = psycopg2.connect(host='localhost', database='ott',
                        user='postgres', password='saritha')
cursor = conn.cursor()
user_id = 0


@app.route('/')
def hello_world():
    return render_template('signin.html')

@app.route('/register_form')
def rform():
    return render_template('register.html')

@app.route('/register', methods=['post'])
def register():
    print("Hello")
    if request.method == 'POST':
        name = request.form.get('name')
        phone_number = request.form.get('phone_number')
        email = request.form.get('email')
        password = request.form.get('password')
        created_datetime=date.today()
        cursor.execute('select count(*) from ott.users')
        result = cursor.fetchone()
        count = result[0]+1
        insert_query = """ INSERT INTO ott.users(user_id,name,email,password,phone_number,created_datetime,is_premium) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
        try:
            record = (int(count), name, email, password, int(phone_number),created_datetime, False)
            cursor.execute(insert_query, record)
            conn.commit()
            count = cursor.rowcount
            print(count, "Record inserted successfully into user table")
            session['phone_number']=phone_number
        except:
            return "Invalid details"
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    phone_number = request.form.get('phone_number')
    password = request.form.get('password')
    try:
        phone_number = int(phone_number)
    except:
        return "Invalid details"
    if phone_number and password: 
        query = "select * from ott.users where phone_number = {0} ".format(phone_number)
        cursor.execute(query)
        print(query)
        result = cursor.fetchone()
        print(result)
        if result is None:
            return "Invalid Details"
        pswd = result[3]
        is_premium=result[6]
        if pswd == password:
            uname=result[1]
            session['phone_number']=phone_number
            query="select * from ott.preference_list where user_id={0}".format(result[0])
            cursor.execute(query)
            result=cursor.fetchall()
            print(result)
            return render_template('user.html',name=uname,pre_list=result,is_premium=is_premium)
        else:
            return "Invalid details"
    return "OK Check"

@app.route('/delete_account')
def delete():
    if 'phone_number' in session:
        phone_number=session['phone_number']
        query="delete from ott.users where phone_number = {0}".format(phone_number)
        print(query)
        cursor.execute(query)
        conn.commit()
        count = cursor.rowcount
        print(count, "Record deleted ")
        return "Deleted succesfully"
    return "Invalid user"

@app.route('/get_all_photos')
def get_photos():
    if 'phone_number' in session:
        query="select user_id from ott.users where phone_number = {0}".format(session['phone_number'])
        cursor.execute(query)
        print(query)
        if cursor.pgresult_ptr is not None:
            uid=cursor.fetchone()
            query="select * from ott.group where user_id={0}".format(uid[0])
            cursor.execute(query)
            print(query)
            result=cursor.fetchall()
            print(result)
            return dumps(result,default=str)
    return jsonify("")

@app.route('/premium',methods=['post'])
def update_premum():
    if 'phone_number' in session:
        mob=session['phone_number']
        cd=request.form.get('credit_card')
        periods=request.form.get('subscription_period')
        start_date=date.today()
        print(str(start_date),str(cd),periods,mob)
        update_query="update  ott.users set is_premium=true where phone_number = {0}".format(mob)
        cursor.execute(update_query)
        cursor.execute('select user_id from ott.users where phone_number = {0}'.format(mob))
        uid=cursor.fetchone()[0]
        insert_query="insert into ott.premium_user values ({0},'{1}',{2},{3},'{4}')".format(uid,start_date,cd,1,periods)
        cursor.execute(insert_query)
        conn.commit()   
        return "Subscibed succesfully"
    return "Invalid page"

if __name__ == '__main__':
    app.run(debug=True)
