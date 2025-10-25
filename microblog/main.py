import datetime
import dateutil.tz

from flask import Blueprint, render_template


from . import model

bp = Blueprint("main", __name__)



@bp.route("/")
def index():
    user = model.User(1, "mary@example.com", "mary")
    posts = [
        model.Post(1, user, "X Works", datetime.datetime.now(dateutil.tz.tzlocal())),
        model.Post(2, user, "This is what the NFL took from us", datetime.datetime.now(dateutil.tz.tzlocal())),
        model.Post(3, user, "X is back down again", datetime.datetime.now(dateutil.tz.tzlocal())),
    ]
    # if your Post supports extra fields, you can enrich them in Jinja context
    # by mapping to dicts before render_template. Otherwise keep it simple.
    return render_template("main/index.html", posts=[
        {
            "user": {"name": "Elon Musk", "handle": "elonmusk"},
            "avatar_url": "",
            "timestamp": "7h",
            "text": "X Works",
            "image_url": "",
            "replies": "398", "retweets": "4.1K", "likes": "11.2K", "saves": "11.2K",
            "is_reply": False
        },
        {
            "user": {"name": "Barstool Sports", "handle": "barstoolsports"},
            "avatar_url": "",
            "timestamp": "Oct 19",
            "text": "This is what the NFL took from us",
            "image_url": "https://pbs.twimg.com/media/F_P1E6wWkAAKZCX.jpg",
            "replies": "398", "retweets": "4.1K", "likes": "11.2K", "saves": "11.2K",
            "is_reply": False
        },
        {
            "user": {"name": "GQ", "handle": "GQ"},
            "avatar_url": "",
            "timestamp": "6h",
            "text": "",
            "image_url": "",
            "replies": "398", "retweets": "4.1K", "likes": "11.2K", "saves": "11.2K",
            "is_reply": True,
            "replying_to": "elonmusk",
            "reply_text": "X is back down again"
        },
    ])


@bp.route("/user")
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

@bp.route("/post")
def post_view():
    author = model.User(3, "collin@example.com", "Collin")

    # The main post
    post = {
        "id": 101,
        "user": {"name": author.name, "handle": "celo2759"},
        "timestamp": "6h",
        "text": "certified bag fumbler",
        "image_url": "",   # leave empty if no image
        "replies": "12", "retweets": "4", "likes": "37", "saves": "2",
    }

    # A couple of response posts
    responses = [
        {
            "user": {"name": "Alice", "handle": "alice"},
            "timestamp": "5h",
            "text": "lol same 😅",
            "image_url": "",
            "replies": "1", "retweets": "0", "likes": "5", "saves": "0",
        },
        {
            "user": {"name": "Bob", "handle": "bob"},
            "timestamp": "4h",
            "text": "Tomorrow’s another shot. Keep going! 💪",
            "image_url": "",
            "replies": "0", "retweets": "1", "likes": "12", "saves": "1",
        },
    ]

    return render_template("main/post.html", post=post, responses=responses)
