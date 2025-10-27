from flask import Blueprint, render_template, request, redirect, url_for, abort
import flask_login

from . import model
from . import db

bp = Blueprint("main", __name__)

@bp.route("/")
@flask_login.login_required
def index():
    query = db.select(model.Post).order_by(model.Post.timestamp.desc()).limit(10)
    posts = db.session.execute(query).scalars().all()
    return render_template("main/index.html", posts=posts)


@bp.route("/new_post", methods=["POST"])
@flask_login.login_required
def new_post():
    text = request.form.get("text")

    response_to = request.form.get("response_to")
    if response_to:
        response_to = db.session.get(model.Post, response_to)
        if not response_to:
            abort(404, "Response to post id {} doesn't exist.".format(response_to))
        post = model.Post(user=flask_login.current_user, text=text, response_to=response_to)
    
    else:
        post = model.Post(user=flask_login.current_user, text=text)

    db.session.add(post)
    db.session.commit()

    if response_to:
        return redirect(url_for("main.post", post_id=response_to.id))
    else:
        return redirect(url_for("main.post", post_id=post.id))


@bp.route("/user/<int:user_id>")
@flask_login.login_required
def user_profile(user_id):
    user = db.session.get(model.User, user_id)
    if not user:
        abort(404, "User id {} doesn't exist.".format(user_id))
    
    # Get all posts by this user, sorted by most recent first
    query = db.select(model.Post).where(model.Post.user_id == user_id).order_by(model.Post.timestamp.desc())
    posts = db.session.execute(query).scalars().all()
    
    return render_template("main/profile.html", user=user, posts=posts)

@bp.route("/post/<int:post_id>")
@flask_login.login_required
def post(post_id):
    post = db.session.get(model.Post, post_id)
    if not post:
        abort(404, "Post id {} doesn't exist.".format(post_id))
    
    # Get responses to this post
    query = db.select(model.Post).where(model.Post.response_to_id == post_id)
    responses = db.session.execute(query).scalars().all()
    
    return render_template("main/post.html", post=post, responses=responses)
