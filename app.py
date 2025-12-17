from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nba.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(200))

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    position = db.Column(db.String(20))
    points = db.Column(db.Integer)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    player_ids = db.Column(db.String(200))

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed = generate_password_hash(password)
        user = User(username=username, password=hashed)
        db.session.add(user)
        db.session.commit()
        flash('Account created')
        return redirect(url_for('login'))
    return render_template('form.html', title='Sign Up', action='signup')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        flash('Invalid login')
    return render_template('form.html', title='Login', action='login')

@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    teams = Team.query.filter_by(user_id=session['user_id']).all()
    players = Player.query.all()
    return render_template('dashboard.html', teams=teams, players=players)

@app.route("/create", methods=['POST'])
def create_team():
    name = request.form.get('team_name')
    p1 = request.form.get('player1')
    p2 = request.form.get('player2')
    p3 = request.form.get('player3')
    team = Team(name=name, user_id=session['user_id'], player_ids=f"{p1},{p2},{p3}")
    db.session.add(team)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if Player.query.count() == 0:
            players = [
                Player(name='LeBron James', position='SF', points=27),
                Player(name='Stephen Curry', position='PG', points=30),
                Player(name='Kevin Durant', position='SF', points=28),
                Player(name='Giannis', position='PF', points=31),
                Player(name='Luka Doncic', position='PG', points=29),
            ]
            for p in players:
                db.session.add(p)
            db.session.commit()
    app.run(debug=True)