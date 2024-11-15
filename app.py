from flask import Flask, render_template
from SofaScore.database import Season
# from database import DataBase
# from user import Session, User


# db = DataBase()
# session = Session()

app = Flask(__name__)


@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/download/<path:season>')
def download(season: str):
    season = Season()

# @app.get('/register')
# def register_get():

#     if session.is_authenticated():
#         return render_template('index.html', message = 'Already registered')

#     return render_template('register.html')

# @app.post('/register')
# def register_post():

#     username = request.form.get('username')
#     email = request.form.get('email')
#     password = request.form.get('password')

#     if User.objects.exists()

#     db.register(
#         username = username,
#         email = email,
#         password = password
#     )

#     session.user = User(username, email, password)

#     return redirect(url_for('index_page'))

# @app.get('/login')
# def login_get():
#     return render_template('login.html')

# @app.post('/login')
# def login_post():
#     return '<h1>Você enviou as credencias para fazer login</h1>'
