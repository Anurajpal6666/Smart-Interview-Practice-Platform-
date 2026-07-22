from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) 
app.secret_key = "spider man and Batman er Pussy"  

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_BINDS"] = {
    "problems": "sqlite:///problems.db"
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Database Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(129), unique=True, nullable=False)
    password_hash = db.Column(db.String(257), nullable=False)
    name = db.Column(db.String(129), nullable=False)

class Problem(db.Model):
    __bind_key__ = "problems"
    id=db.Column(db.Integer, primary_key=True)
    frontendQuestionId=db.Column(db.String(8),nullable=False)
    title=db.Column(db.String(299),nullable=False)
    topicTags=db.Column(db.Text,nullable=False)
    difficulty=db.Column(db.String(8),nullable=False)
    acRate=db.Column(db.Float,nullable=False)
    isFavor=db.Column(db.Boolean,nullable=False)
    paidOnly=db.Column(db.Boolean,nullable=False)

class SolvedProblem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)

    problem_id = db.Column(db.Integer, nullable=False)

class FavoriteProblem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    problem_id = db.Column(db.Integer, nullable=False)

# Create Database
with app.app_context():
    db.create_all()


# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):

            session["user"] = user.name
            session["email"] = user.email

            return redirect(url_for("dashboard"))

        else:
            return redirect(url_for("login"))

    return render_template("login.html")

#register
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")
        name = request.form.get("name")

        user = User.query.filter_by(email=email).first()

        if user:
            return redirect(url_for("register"))

        new_user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")
# Dashboard
@app.route("/dashboard")
def dashboard():

    if "user" in session:
        return render_template("dashboard.html", user=session["user"])
    return redirect(url_for("login"))


# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))

#problem
@app.route('/porblem')
def problem():
    all_problme=Problem.query.all()
    return render_template("problems.html",problem=all_problme)

@app.route("/favorite/<int:problem_id>")
def add_favorite(problem_id):

    if "email" not in session:
        return redirect(url_for("login"))

    user = User.query.filter_by(
        email=session["email"]
    ).first()

    already = FavoriteProblem.query.filter_by(
        user_id=user.id,
        problem_id=problem_id
    ).first()

    if not already:

        fav = FavoriteProblem(
            user_id=user.id,
            problem_id=problem_id
        )

        db.session.add(fav)
        db.session.commit()

    return redirect(url_for("problem"))

#profile
@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template(
        "profile.html",
        name=session["user"],
        email=session.get("email")
    )
    
#favorites
# @app.route("/favorites")
# def favorites():
#     return render_template("favorites.html", favorites=[])

@app.route("/favorites")
def favorites():

    if "email" not in session:
        return redirect(url_for("login"))

    user = User.query.filter_by(
        email=session["email"]
    ).first()

    favs = FavoriteProblem.query.filter_by(
        user_id=user.id
    ).all()

    favorite_list = []

    for fav in favs:

        pro = Problem.query.get(fav.problem_id)

        if pro:
            favorite_list.append(pro)

    return render_template(
        "favorites.html",
        favorites=favorite_list
    )
#process
@app.route("/process")
def process():
    return render_template("process.html")

# @app.route("/achievements")
# def achievements():
#     return render_template("achievements.html")

#achievements
@app.route("/achievements")
def achievements():

    if "email" not in session:
        return redirect(url_for("login"))

    user = User.query.filter_by(
        email=session["email"]
    ).first()

    solved = SolvedProblem.query.filter_by(
        user_id=user.id
    ).count()

    total = Problem.query.count()

    percent = 0

    if total > 0:
        percent = round((solved / total) * 100)

    return render_template(
        "achievements.html",
        solved=solved,
        total=total,
        percent=percent
    )

@app.route("/settings")
def settings():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template(
        "settings.html",
        name=session["user"],
        email=session["email"]
    )

@app.route("/change_password", methods=["POST"])
def change_password():

    if "email" not in session:
        return redirect(url_for("login"))

    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    user = User.query.filter_by(email=session["email"]).first()

    if not check_password_hash(user.password_hash, current_password):
        return redirect(url_for("settings"))

    if new_password != confirm_password:
        return redirect(url_for("settings"))

    user.password_hash = generate_password_hash(new_password)

    db.session.commit()

    return redirect(url_for("settings"))

if __name__ == "__main__":
    app.run(debug=True)