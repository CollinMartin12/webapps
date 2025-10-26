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
    post = model.Post(user=flask_login.current_user, text=text)
    db.session.add(post)
    db.session.commit()
    return redirect(url_for("main.post", post_id=post.id))


@bp.route("/user")
@flask_login.login_required
def user_profile():
    # Test user for the profile view
    user = {
        "name": "John Doe",
        "handle": "johndoe",
        "bio": (
            "Web developer passionate about creating amazing user experiences. "
            "Love coding, coffee, and sharing knowledge with the community. "
            "Always learning something new! 🚀"
        ),
        "stats": {"following": 156, "followers": 1234, "posts": 89},
    }

    # Two example posts by this user
    posts = [
        {
            "user": {"name": "John Doe", "handle": "johndoe"},
            "timestamp": "1h",
            "text": (
                "Just deployed my latest project! It's a React app with TypeScript and Tailwind CSS. "
                "The development experience has been amazing. Check it out! #React #TypeScript #TailwindCSS"
            ),
            "image_url": "",
            "replies": "15", "retweets": "120", "likes": "980", "saves": "44",
        },
        {
            "user": {"name": "John Doe", "handle": "johndoe"},
            "timestamp": "3h",
            "text": (
                'Reading "Clean Code" by Robert Martin. Every developer should read it at least once.'
            ),
            "image_url": "",
            "replies": "9", "retweets": "32", "likes": "210", "saves": "11",
        },
    ]

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
