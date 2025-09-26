import os
from datetime import datetime

from flask import (Flask, flash, g, redirect, render_template, request,
                   session, url_for)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "quiz.db")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("APP_SECRET_KEY", "change-me")
app.config["ADMIN_PASSWORD"] = os.environ.get("APP_ADMIN_PASSWORD", "admin")

db = SQLAlchemy(app)


class Competition(db.Model):
    __tablename__ = "competitions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    topics = db.relationship("Topic", cascade="all, delete-orphan", backref="competition")


class Topic(db.Model):
    __tablename__ = "topics"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey("competitions.id"), nullable=False)
    questions = db.relationship("Question", cascade="all, delete-orphan", backref="topic")


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=False)


@app.before_request
def create_tables_and_set_globals():
    db.create_all()
    g.competition_count = db.session.execute(db.select(func.count(Competition.id))).scalar()
    g.topic_count = db.session.execute(db.select(func.count(Topic.id))).scalar()
    g.question_count = db.session.execute(db.select(func.count(Question.id))).scalar()


def is_admin_authenticated() -> bool:
    return session.get("is_admin") is True


@app.context_processor
def inject_globals():
    return {
        "is_admin_authenticated": is_admin_authenticated(),
        "competition_count": getattr(g, "competition_count", 0),
        "topic_count": getattr(g, "topic_count", 0),
        "question_count": getattr(g, "question_count", 0),
    }


@app.route("/")
def home():
    return redirect(url_for("list_competitions"))


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == app.config["ADMIN_PASSWORD"]:
            session["is_admin"] = True
            flash("Logged in as admin.", "success")
            return redirect(url_for("admin_dashboard"))
        flash("Incorrect password.", "error")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    flash("Logged out.", "info")
    return redirect(url_for("admin_login"))


@app.route("/admin")
def admin_dashboard():
    if not is_admin_authenticated():
        return redirect(url_for("admin_login"))
    competitions = Competition.query.order_by(Competition.created_at.desc()).all()
    return render_template("admin_dashboard.html", competitions=competitions)


@app.route("/admin/competition/new", methods=["POST"])
def create_competition():
    if not is_admin_authenticated():
        return redirect(url_for("admin_login"))
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    if not name:
        flash("Competition name is required.", "error")
        return redirect(url_for("admin_dashboard"))
    competition = Competition(name=name, description=description)
    db.session.add(competition)
    db.session.commit()
    flash("Competition created.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/competition/<int:competition_id>")
def view_competition(competition_id: int):
    if not is_admin_authenticated():
        return redirect(url_for("admin_login"))
    competition = Competition.query.get_or_404(competition_id)
    topics = Topic.query.filter_by(competition_id=competition_id).all()
    return render_template("admin_competition.html", competition=competition, topics=topics)


@app.route("/admin/competition/<int:competition_id>/topic", methods=["POST"])
def create_topic(competition_id: int):
    if not is_admin_authenticated():
        return redirect(url_for("admin_login"))
    competition = Competition.query.get_or_404(competition_id)
    title = request.form.get("title", "").strip()
    if not title:
        flash("Topic title is required.", "error")
        return redirect(url_for("view_competition", competition_id=competition.id))
    topic = Topic(title=title, competition_id=competition.id)
    db.session.add(topic)
    db.session.commit()
    flash("Topic created.", "success")
    return redirect(url_for("view_competition", competition_id=competition.id))


@app.route("/admin/topic/<int:topic_id>")
def view_topic(topic_id: int):
    if not is_admin_authenticated():
        return redirect(url_for("admin_login"))
    topic = Topic.query.get_or_404(topic_id)
    questions = Question.query.filter_by(topic_id=topic.id).all()
    return render_template("admin_topic.html", topic=topic, questions=questions)


@app.route("/admin/topic/<int:topic_id>/question", methods=["POST"])
def create_question(topic_id: int):
    if not is_admin_authenticated():
        return redirect(url_for("admin_login"))
    topic = Topic.query.get_or_404(topic_id)
    prompt = request.form.get("prompt", "").strip()
    option_a = request.form.get("option_a", "").strip()
    option_b = request.form.get("option_b", "").strip()
    option_c = request.form.get("option_c", "").strip()
    option_d = request.form.get("option_d", "").strip()
    correct_option = request.form.get("correct_option", "").strip().upper()

    if not all([prompt, option_a, option_b, option_c, option_d, correct_option]):
        flash("All fields are required to create a question.", "error")
        return redirect(url_for("view_topic", topic_id=topic.id))

    if correct_option not in {"A", "B", "C", "D"}:
        flash("Correct option must be A, B, C, or D.", "error")
        return redirect(url_for("view_topic", topic_id=topic.id))

    question = Question(
        prompt=prompt,
        option_a=option_a,
        option_b=option_b,
        option_c=option_c,
        option_d=option_d,
        correct_option=correct_option,
        topic_id=topic.id,
    )
    db.session.add(question)
    db.session.commit()
    flash("Question added.", "success")
    return redirect(url_for("view_topic", topic_id=topic.id))


@app.route("/admin/clear", methods=["POST"])
def clear_all_data():
    if not is_admin_authenticated():
        return redirect(url_for("admin_login"))
    Question.query.delete()
    Topic.query.delete()
    Competition.query.delete()
    db.session.commit()
    flash("All competitions, topics, and questions have been removed.", "info")
    return redirect(url_for("admin_dashboard"))


@app.route("/competitions")
def list_competitions():
    competitions = Competition.query.order_by(Competition.created_at.desc()).all()
    return render_template("competitions.html", competitions=competitions)


@app.route("/competitions/<int:competition_id>/topics")
def list_topics(competition_id: int):
    competition = Competition.query.get_or_404(competition_id)
    topics = Topic.query.filter_by(competition_id=competition.id).all()
    return render_template("topics.html", competition=competition, topics=topics)


@app.route("/quiz/<int:topic_id>")
def quiz(topic_id: int):
    topic = Topic.query.get_or_404(topic_id)
    questions = Question.query.filter_by(topic_id=topic.id).order_by(Question.id).all()
    if not questions:
        flash("This topic has no questions yet.", "error")
        return redirect(url_for("list_topics", competition_id=topic.competition_id))

    try:
        index = int(request.args.get("q", 1)) - 1
    except ValueError:
        index = 0
    index = max(0, min(index, len(questions) - 1))
    question = questions[index]

    previous_question = None
    next_question = None
    if index > 0:
        previous_question = questions[index - 1]
    if index < len(questions) - 1:
        next_question = questions[index + 1]

    return render_template(
        "quiz.html",
        topic=topic,
        question=question,
        index=index,
        total=len(questions),
        previous_index=index if previous_question else None,
        next_index=index + 2 if next_question else None,
    )


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
