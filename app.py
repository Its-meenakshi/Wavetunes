import os
import uuid
from functools import wraps
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

AVATAR_DIR = os.path.join(app.static_folder, "images", "avatars")
os.makedirs(AVATAR_DIR, exist_ok=True)
ALLOWED_AVATAR_EXT = {"png", "jpg", "jpeg", "gif", "webp"}

# ---------------------------------------------------------------------------
# In-memory "database" -- swap this for a real DB (SQLAlchemy, etc.) later.
# ---------------------------------------------------------------------------
USERS = {}  # email -> {username, email, password_hash, avatar_url}


def seed_demo_user():
    if "demo@wavetunes.app" not in USERS:
        USERS["demo@wavetunes.app"] = {
            "username": "Meenakshi",
            "email": "demo@wavetunes.app",
            "password_hash": generate_password_hash("password123"),
            "avatar_url": None,
        }


seed_demo_user()

MASTER_TRACKS = [
    {"title": "Ocean Drive", "artist": "Nova Reyes", "genre": "Synthwave", "duration": 198, "liked": True, "cover": 0},
    {"title": "Midnight Rain", "artist": "Kilo Sound", "genre": "Lo-Fi", "duration": 224, "liked": False, "cover": 1},
    {"title": "Electric Dreams", "artist": "Parker Vale", "genre": "Pop", "duration": 176, "liked": True, "cover": 2},
    {"title": "Rainy Evenings", "artist": "Soft Static", "genre": "Romantic", "duration": 210, "liked": False, "cover": 3},
    {"title": "Echoes of You", "artist": "Unfinished Chapters", "genre": "Indie", "duration": 189, "liked": True, "cover": 4},
    {"title": "Neon Horizon", "artist": "Nova Reyes", "genre": "Synthwave", "duration": 242, "liked": False, "cover": 5},
    {"title": "Study Haze", "artist": "Kilo Sound", "genre": "Lo-Fi", "duration": 168, "liked": False, "cover": 6},
    {"title": "Heartbeat", "artist": "Parker Vale", "genre": "Pop", "duration": 192, "liked": True, "cover": 7},
    {"title": "Slow Burn", "artist": "Soft Static", "genre": "Romantic", "duration": 235, "liked": False, "cover": 0},
    {"title": "Static Memory", "artist": "Unfinished Chapters", "genre": "Indie", "duration": 179, "liked": False, "cover": 1},
    {"title": "Quiet Hours", "artist": "Halcyon Days", "genre": "Chill", "duration": 260, "liked": True, "cover": 2},
    {"title": "Deep Focus", "artist": "Halcyon Days", "genre": "Focus", "duration": 310, "liked": False, "cover": 3},
    {"title": "Golden Hour", "artist": "Nova Reyes", "genre": "Pop", "duration": 201, "liked": False, "cover": 4},
    {"title": "Velvet Skyline", "artist": "Parker Vale", "genre": "Synthwave", "duration": 214, "liked": True, "cover": 5},
    {"title": "Afterglow", "artist": "Halcyon Days", "genre": "Chill", "duration": 187, "liked": False, "cover": 6},
    {"title": "Paper Boats", "artist": "Soft Static", "genre": "Indie", "duration": 173, "liked": False, "cover": 7},
]


def track_copy(indices):
    """Return deep-enough copies of tracks so per-page like toggles don't collide."""
    return [dict(MASTER_TRACKS[i]) for i in indices]


MOODS = [
    {"name": "Chill Vibes", "icon": "fa-cloud", "count": 42},
    {"name": "Workout", "icon": "fa-dumbbell", "count": 65},
    {"name": "Focus", "icon": "fa-brain", "count": 38},
    {"name": "Party", "icon": "fa-champagne-glasses", "count": 51},
]


def build_playlists():
    return [
        {"name": "Late Night Drives", "icon": "fa-car", "track_count": 5, "duration_label": "19 min",
         "track_indices": [0, 5, 13, 1, 6]},
        {"name": "Deep Focus Mix", "icon": "fa-brain", "track_count": 3, "duration_label": "13 min",
         "track_indices": [11, 6, 10]},
        {"name": "Weekend Feels", "icon": "fa-sun", "track_count": 4, "duration_label": "14 min",
         "track_indices": [2, 7, 12, 3]},
        {"name": "Rainy Day", "icon": "fa-cloud-rain", "track_count": 4, "duration_label": "16 min",
         "track_indices": [3, 8, 15, 4]},
    ]


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_email" not in session:
            flash("Please sign in to continue.", "error")
            return redirect(url_for("signin"))
        return view(*args, **kwargs)
    return wrapped


def current_user():
    email = session.get("user_email")
    return USERS.get(email)


@app.context_processor
def inject_user():
    return {"user": current_user()}


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------
@app.route("/")
def root():
    if "user_email" in session:
        return redirect(url_for("home"))
    return redirect(url_for("signin"))


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = USERS.get(email)
        if user and check_password_hash(user["password_hash"], password):
            session["user_email"] = email
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for("home"))
        flash("Incorrect email or password.", "error")
        return redirect(url_for("signin"))
    return render_template("auth.html", mode="signin")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        if not username or not email or not password:
            flash("Please fill in every field.", "error")
            return redirect(url_for("signup"))
        if password != confirm:
            flash("Passwords don't match.", "error")
            return redirect(url_for("signup"))
        if email in USERS:
            flash("An account with that email already exists.", "error")
            return redirect(url_for("signup"))

        USERS[email] = {
            "username": username,
            "email": email,
            "password_hash": generate_password_hash(password),
            "avatar_url": None,
        }
        session["user_email"] = email
        flash("Account created — welcome to WaveTunes!", "success")
        return redirect(url_for("home"))
    return render_template("auth.html", mode="signup")


@app.route("/logout")
def logout():
    session.pop("user_email", None)
    flash("You've been signed out.", "success")
    return redirect(url_for("signin"))


# ---------------------------------------------------------------------------
# App routes
# ---------------------------------------------------------------------------
@app.route("/home")
@login_required
def home():
    return render_template(
        "index.html",
        active_page="home",
        trending=track_copy([0, 1, 2, 3, 4, 5]),
        made_for_you=track_copy([6, 7, 8, 9]),
    )


@app.route("/discover")
@login_required
def discover():
    return render_template(
        "discover.html",
        active_page="discover",
        new_releases=track_copy([12, 13, 14, 15]),
        recommended=track_copy([0, 2, 5, 7, 10, 11]),
        moods=MOODS,
    )


@app.route("/library")
@login_required
def library():
    tracks = track_copy(range(len(MASTER_TRACKS)))
    genres = sorted({t["genre"] for t in tracks})
    return render_template(
        "library.html",
        active_page="library",
        tracks=tracks,
        genres=genres,
    )


@app.route("/favourites")
@login_required
def favourites():
    tracks = track_copy(range(len(MASTER_TRACKS)))
    return render_template(
        "favourites.html",
        active_page="favourites",
        tracks=tracks,
    )


@app.route("/playlists")
@login_required
def playlists():
    tracks = track_copy(range(len(MASTER_TRACKS)))
    return render_template(
        "playlists.html",
        active_page="playlists",
        tracks=tracks,
        playlists=build_playlists(),
    )


@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html", active_page="settings")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = current_user()

    if request.method == "POST":
        # Avatar upload (separate form, has a file field)
        if "avatar" in request.files and request.files["avatar"].filename:
            file = request.files["avatar"]
            ext = file.filename.rsplit(".", 1)[-1].lower()
            if ext in ALLOWED_AVATAR_EXT:
                filename = secure_filename(f"{uuid.uuid4().hex}.{ext}")
                file.save(os.path.join(AVATAR_DIR, filename))
                user["avatar_url"] = url_for("static", filename=f"images/avatars/{filename}")
                flash("Profile picture updated.", "success")
            else:
                flash("Please upload a PNG, JPG, GIF, or WEBP image.", "error")
            return redirect(url_for("profile"))

        form_name = request.form.get("form_name")

        if form_name == "details":
            new_username = request.form.get("username", "").strip()
            new_email = request.form.get("email", "").strip().lower()
            if not new_username or not new_email:
                flash("Username and email can't be empty.", "error")
                return redirect(url_for("profile"))
            if new_email != user["email"] and new_email in USERS:
                flash("That email is already in use.", "error")
                return redirect(url_for("profile"))

            if new_email != user["email"]:
                USERS.pop(user["email"])
                user["email"] = new_email
                USERS[new_email] = user
                session["user_email"] = new_email
            user["username"] = new_username
            flash("Profile details saved.", "success")
            return redirect(url_for("profile"))

        if form_name == "password":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")
            if not check_password_hash(user["password_hash"], current_password):
                flash("Current password is incorrect.", "error")
            elif new_password != confirm_password:
                flash("New passwords don't match.", "error")
            elif len(new_password) < 6:
                flash("New password must be at least 6 characters.", "error")
            else:
                user["password_hash"] = generate_password_hash(new_password)
                flash("Password updated.", "success")
            return redirect(url_for("profile"))

    return render_template("profile.html", active_page="profile")


if __name__ == "__main__":
    # Render (and most hosts) inject the port to bind to via the PORT env var,
    # and the app must listen on 0.0.0.0, not just localhost.
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
