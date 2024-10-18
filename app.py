from flask import Flask, render_template, redirect, url_for, request, make_response, session, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from my_sqldb import MyDb
import mysql.connector

app = Flask(__name__)

app.config.from_pyfile('config.py')
password ="1"
prin
db = MyDb(app)

login_manager = LoginManager();

login_manager.init_app(app);

login_manager.login_view = 'login'
login_manager.login_message = 'Доступ к данной странице есть только у авторизованных пользователей '
login_manager.login_message_category = 'warning'

def get_roles():
    cursor = db.connect().cursor(named_tuple=True)
    query = ('SELECT * FROM roles')
    cursor.execute(query)
    roles = cursor.fetchall()
    return roles

class User(UserMixin):
    def __init__(self, user_id, user_login):
        self.id = user_id
        self.login = user_login
        

@login_manager.user_loader
def load_user(user_id):
    cursor = db.connect().cursor(named_tuple=True)
    query = ('SELECT * FROM users WHERE id=%s')
    cursor.execute(query,(user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
       return User(user.id,user.login)
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == "POST":
        login = request.form.get('login')
        password = request.form.get('password')
        remember = request.form.get('remember')
        cursor = db.connect().cursor(named_tuple=True)
        query = ('SELECT * FROM users WHERE login=%s and password_hash=SHA2(%s,256) ')
        cursor.execute(query, (login, password))
        user_data = cursor.fetchone()
        if user_data:
            login_user(User(user_data.id,user_data.login),remember=remember)
            flash('Вы успешно прошли аутентификацию', 'success')
            return redirect(url_for('index'))
        flash('Неверные логин или пароль', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/list_users')
@login_required
def list_users():
    cursor = db.connect().cursor(named_tuple=True)
    query = ('SELECT * FROM users')
    cursor.execute(query)
    users = cursor.fetchall()
    return render_template('list_users.html', users = users)

@app.route('/create_user', methods=['GET','POST'])
@login_required
def create_user():

    if request.method == "POST":
        first_name = request.form.get('name')
        second_name = request.form.get('lastname')
        middle_name = request.form.get('middlename')
        login = request.form.get('login')
        password = request.form.get('password')
        role_id = request.form.get('role')


        try:
            cursor = db.connect().cursor(named_tuple=True)
            query = ('INSERT INTO users (login, password_hash, first_name, second_name, middle_name, role_id) values(%s, SHA2(%s,256), %s, %s, %s, %s) ')
            cursor.execute(query,(login, password, first_name, second_name, middle_name, role_id))
            db.connect().commit()
            flash('Вы успешно зарегестировали пользователя', 'success')
            return redirect(url_for('list_users'))
        except mysql.connector.errors.DatabaseError:
            db.connect().rollback()
            flash('Ошибка при регистрации', 'danger')

    roles = get_roles()
    return render_template('create_user.html', roles = roles)

@app.route('/show_user/<int:user_id>')
@login_required
def show_user(user_id):
    cursor = db.connect().cursor(named_tuple=True)
    query = ('SELECT users.*, roles.name as role_name FROM users LEFT JOIN roles ON users.role_id = roles.id WHERE users.id = %s')
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    print(user)
    return render_template('show_user.html', user = user )


@app.route('/edit_user/<int:user_id>', methods=['GET','POST'])
@login_required
def edit_user(user_id):
    filtered_errors = {}

    cursor = db.connect().cursor(named_tuple=True)
    query = ('SELECT users.*, roles.name as role_name FROM users LEFT JOIN roles ON users.role_id = roles.id WHERE users.id = %s')
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()

    if request.method == "POST":
        first_name = request.form.get('name')
        second_name = request.form.get('lastname')
        middle_name = request.form.get('middlename')

        try:
            cursor = db.connect().cursor(named_tuple=True)
            query = ('UPDATE users SET first_name=%s, second_name=%s, middle_name=%s where id=%s;')
            cursor.execute(query,(first_name,  second_name, middle_name, user_id))
            db.connect().commit()
            flash('Вы успешно обновили пользователя', 'success')
            return redirect(url_for('list_users'))
        except mysql.connector.errors.DatabaseError:
            db.connect().rollback()
            flash('Ошибка при обновлении', 'danger')
    return render_template('edit_user.html', user = user, filtered_errors=filtered_errors)

@app.route('/delete_users/<int:user_id>', methods=['GET','POST'])
@login_required
def delete_user(user_id):
    if request.method == "POST":
        try:
            cursor = db.connect().cursor(named_tuple=True)
            query = ('DELETE FROM users WHERE id=%s')
            cursor.execute(query, (user_id,))
            db.connect().commit()
            flash('Удаление успешно', 'success')
        except:
            db.connect().rollback()
            flash('Ошибка при удалении пользователя', 'danger')
    return redirect(url_for('list_users'))

if __name__ == "__main__":
    app.run(debug=True)
