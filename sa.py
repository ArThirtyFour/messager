import os
import sqlite3

import datetime
import hashlib

from flask import Flask, render_template , redirect , request , session

bd=sqlite3.connect('users.db',check_same_thread=False)
cursor = bd.cursor()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(20).hex()
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)


@app.route('/')
def da():
    if 'loginned' in session:
        all_text = cursor.execute('SELECT * FROM pasta').fetchall()
        return render_template('main.html',name_user=session['user_name'] , text=all_text) 
    else:
        return redirect('/register')


@app.route('/login',methods=['GET','POST'])
def login():
    if  request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST': 
        login = request.form['login'].lower()
        password = hashlib.md5(request.form['password'].encode()).hexdigest()
        try:
            info = cursor.execute('SELECT * FROM users WHERE login = ?',(login,)).fetchone()
            bd_pass = info[1]
        except TypeError:
            info = 'Отсуствует'

        if info == 'Отсуствует':
            return 'ЛОГИНА НЕТ!'
        else:
            if bd_pass == password:
                session.permanent = True
                session['loginned'] = 'Yes'
                session['user_name'] = login
                return redirect('/')
            elif bd_pass != password:
                return f'НЕВЕРНО'

@app.route('/register',methods=['GET','POST'])
def register():
    if  request.method == 'GET':
        return render_template('register.html')   
    elif request.method == 'POST':
        login = request.form['login'].lower()
        password = hashlib.md5(request.form['password'].encode()).hexdigest()
        try:
            cursor.execute('INSERT INTO users VALUES (?,?)',(login,password))
            bd.commit()
            session.permanent = True
            session['loginned'] = 'Yes'
            session['user_name'] = login
            return redirect ('/')
        except sqlite3.IntegrityError:
            return 'ДА ТАКАЯ ЗАПИСЬ УЖЕ ЕСТЬ <a href=/register> РЕГИСТРАЦИЯ</a>'


@app.route('/logout')
def dae():
    if session['loginned'] == 'Yes':
        session.permanent = True
        session.pop('loginned', None)
        session.pop('user_name', None)
        print(session)
        return redirect ('/login')


@app.route('/add',methods=['GET','POST'])
def add_paste():
    session.permanent = True
    if 'loginned' not in session:
        return redirect('/login')
    else:
        if request.method == 'GET':
            return render_template('add.html')
        if request.method == 'POST':
            session.permanent = True
            text = request.form['text']
            name = session['user_name']
            cursor.execute('INSERT INTO pasta VALUES(?,?)',(text,name))
            bd.commit()
            return redirect('/')

        




@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')





if __name__ == '__main__':
    app.run(debug=True)
