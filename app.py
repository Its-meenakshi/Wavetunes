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
# Tracks, moods, playlists (unchanged)
# ---------------------------------------------------------------------------
MASTER_TRACKS = [
    {"title": "Ocean Drive", "artist": "Nova Reyes", "genre": "Synthwave", "duration": 198, "liked": True, "cover": 0},
    # ... keep the rest of your tracks here ...
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
        # ... keep the rest of your playlists here ...
    ]

# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------
def login_required(view):
    from functools import wraps
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
# ... keep all your existing route definitions here ...

# ---------------------------------------------------------------------------
# Run app (Render fix)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
