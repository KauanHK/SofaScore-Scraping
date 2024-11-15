from flask import Flask, render_template, request, Response
from SofaScore.database import Season, Tournament
import csv
import io
import os
# from database import DataBase
# from user import Session, User


# db = DataBase()
# session = Session()

app = Flask(__name__)


@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/download/<path:tournament>/<path:season>')
def download(tournament: str, season: str):

    file_path = f'SofaScore/matches/{season.replace('/', '-')}.csv'

    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = list(csv.reader(f))
        return Response(
            stringify(data),
            mimetype="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={season.replace(' ', '_')}.csv"
            }
        )
    
    season_id = Season.get_id(tournament, season)
    t_id = Season.get_tournament_id(tournament)

    s = Season(season_id, season, Tournament(t_id, tournament))
    rounds = s.load(int(request.args['rounds']))
    for round in rounds:
        for match in round.load():
            match.save()

    with open(file_path, 'r') as f:
        data = list(csv.reader(f))

    csv_data = stringify(data)

    response = Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={season.replace(' ', '_')}_rodadas_{rounds}.csv"
        }
    )
    return response

def stringify(data) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(data)
    csv_data = output.getvalue()
    output.close()
    return csv_data

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
