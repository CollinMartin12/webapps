from flask import Blueprint, render_template, request, redirect, url_for, abort
import flask_login
from sqlalchemy.orm import selectinload, aliased


from . import model
from . import db

bp = Blueprint("main", __name__)

@bp.route("/")
@flask_login.login_required
def index():
    # --- Latest top-level posts (already had) ---
    latest_query = (
        db.select(model.Post)
        .where(model.Post.response_to == None)
        .order_by(model.Post.timestamp.desc())
        .limit(10)
    )
    latest_posts = db.session.execute(latest_query).scalars().all()

    # --- Latest top-level posts from people the current user follows ---
    followers = aliased(model.User)  # alias for the follower side
    following_query = (
        db.select(model.Post)
        .join(model.User)                                   # Post -> Author
        .join(followers, model.User.followers)              # Author -> Followers (aliased)
        .where(followers.id == flask_login.current_user.id) # keep posts whose author is followed by me
        .where(model.Post.response_to == None)            # only top-level posts
        .order_by(model.Post.timestamp.desc())
        .limit(10)
    )
    following_posts = db.session.execute(following_query).scalars().all()

    return render_template(
        "main/index.html",
        latest_posts=latest_posts,
        following_posts=following_posts,
    )

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
    user = db.session.execute(
        db.select(model.User)
        .options(
            selectinload(model.User.followers),
            selectinload(model.User.following),
        )
        .where(model.User.id == user_id)
    ).scalar_one_or_none() 

    if not user:
        abort(404, "User id {} doesn't exist.".format(user_id))
    

    viewer = db.session.get(model.User, flask_login.current_user.id)

    # SAFEST: compare by IDs
    is_self = (user.id == viewer.id)
    is_following = any(f.id == viewer.id for f in user.followers)

    if is_self:
        follow_button = "none"
    elif is_following:
        follow_button = "unfollow"
    else:
        follow_button = "follow"
    # Get all posts by this user, sorted by most recent first
        
    query = db.select(model.Post).where(model.Post.user_id == user_id and model.Post.response_to == None).order_by(model.Post.timestamp.desc())
    posts = db.session.execute(query).scalars().all()
    
    return render_template("main/profile.html", user=user, posts=posts, follow_button = follow_button)

@bp.route("/post/<int:post_id>")
@flask_login.login_required
def post(post_id):
    post = db.session.get(model.Post, post_id)
    if not post:
        abort(404, "Post id {} doesn't exist.".format(post_id))
    if post.response_to != None:
        abort(403, "Post{} is response")
    
    # Get responses to this post
    query = db.select(model.Post).where(model.Post.response_to_id == post_id)
    responses = db.session.execute(query).scalars().all()
    
    return render_template("main/post.html", post=post, responses=responses)


# app/main/routes.py (or wherever your main blueprint lives)



@bp.route("/follow/<int:user_id>", methods=["POST"])
@flask_login.login_required
def follow(user_id: int):
    """
    Make the current user follow another user (user_id).
    Rules:
      - 404 if the user to follow doesn't exist
      - 403 if current user == user to follow
      - 403 if already following
    """
    user = db.session.get(model.User, user_id)
    if user is None:
        abort(404)

    if user.id == flask_login.current_user.id:
        redirect(url_for('main.user_profile', user_id = user_id))

    if flask_login.current_user in user.followers:
        redirect(url_for("main.user_profile", user_id = user_id))

    # Establish the follow relationship
    user.followers.append(flask_login.current_user)
    db.session.commit()

    return redirect(url_for("main.user_profile", user_id=user.id))


@bp.route("/unfollow/<int:user_id>", methods=["POST"])
@flask_login.login_required
def unfollow(user_id: int):
    """
    Make the current user unfollow another user (user_id).
    Rules:
      - 404 if the user to unfollow doesn't exist
      - 403 if current user == user to unfollow
      - 403 if not currently following
    """
    user = db.session.get(model.User, user_id)
    if user is None:
        abort(404)

    if user.id == flask_login.current_user.id:
        redirect(url_for("main.user_profile", user_id = user_id))


    if flask_login.current_user not in user.followers:
        redirect(url_for("main.user_profile", user_id = user_id))

    # Remove the follow relationship
    user.followers.remove(flask_login.current_user)
    db.session.commit()

    return redirect(url_for("main.user_profile", user_id=user.id))