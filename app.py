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
app.secret_key = "dev-secret-key-change-me"  # replace with a real secret in production

AVATAR_DIR = os.path.join(app.static_folder, "images", "avatars")
os.makedirs(AVATAR_DIR, exist_ok=True)
ALLOWED_AVATAR_EXT = {"png", "jpg", "jpeg", "gif", "webp"}

# ---------------------------------------------------------------------------
# In-memory "database"
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

# ---------------------------------------------------------------------------
# Tracks, moods, playlists
# ---------------------------------------------------------------------------
MASTER_TRACKS = [
    {"title": "Ocean Drive", "artist": "Nova Reyes", "genre": "Synthwave", "duration": 198, "liked": True, "cover": 0},
    {"title": "Midnight Rain", "artist": "Kilo Sound", "genre": "Lo-Fi", "duration": 224, "liked": False, "cover": 1},
    {"title": "Electric Dreams", "artist": "Parker Vale", "genre": "Pop", "duration": 176, "liked": True, "cover": 2},
    # ... keep all your tracks here ...
]

def track_copy(indices):
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
# Routes (signin, signup, logout, home, discover, library, favourites, playlists, settings, profile)
# ---------------------------------------------------------------------------
@app.route("/")
def root():
    if "user_email" in session:
        return redirect(url_for("home"))
    return redirect(url_for("signin"))

@app.route("/signin", methods=["GET", "POST"])
def signin():
    # ... keep your signin logic ...
    return render_template("auth.html", mode="signin")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    # ... keep your signup logic ...
    return render_template("auth.html", mode="signup")

@app.route("/logout")
def logout():
    session.pop("user_email", None)
    flash("You've been signed out.", "success")
    return redirect(url_for("signin"))

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
    # ... keep your profile logic ...
    return render_template("profile.html", active_page="profile")

# ---------------------------------------------------------------------------
# Run app (Render fix)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
