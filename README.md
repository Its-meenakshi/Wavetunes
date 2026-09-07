# 🎵 WaveTunes

A Spotify-inspired music streaming web app built with **Flask**, **Jinja2**, and vanilla **HTML/CSS/JS**. Sign up, sign in, browse trending tracks, build playlists, like favourites, and manage your profile — all wrapped in a dark, minimal, teal-and-violet UI.

**Live demo:** https://wavetunes-7.onrender.com

---

## Features

- **Sign up / Sign in** — the landing page, with session-based authentication
- **Home** — hero section, trending tracks, and personalized picks
- **Discover** — new releases, recommendations, and mood-based browsing
- **Library** — full track list with search, genre filters, sorting, and list/grid views
- **Favourites** — all liked tracks in one place
- **Playlists** — browse curated playlists and their tracks
- **Profile** — edit username, email, password, and upload a profile picture
- **Settings** — theme, notification, and playback preferences
- **Mini player** — persistent footer player with play/pause/skip and a progress bar (currently plays a demo tone per track — see [Known Limitations](#known-limitations))

---

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | Flask, Jinja2, Werkzeug (password hashing) |
| Frontend | HTML, CSS (custom properties / no framework), vanilla JS |
| Server (production) | Gunicorn |
| Data | In-memory Python dicts (no database yet — see below) |

---

## Project Structure

```
wavetunes/
├── app.py                  # Flask routes, auth, demo data
├── requirements.txt
├── Procfile                 # gunicorn start command for deployment
├── render.yaml               # optional Render Blueprint config
├── runtime.txt                # pinned Python version
├── templates/
│   ├── base.html              # shared sidebar / navbar / footer player
│   ├── auth.html               # sign in + sign up
│   ├── index.html               # home
│   ├── discover.html
│   ├── library.html
│   ├── favourites.html
│   ├── playlists.html
│   ├── settings.html
│   └── profile.html
└── static/
    ├── css/style.css
    ├── js/player.js            # shared footer player logic
    └── images/avatars/          # uploaded profile pictures
```

---

## Running Locally

**Requirements:** Python 3.12+

```bash
git clone https://github.com/its-meenakshi/Wavetunes.git
cd Wavetunes
pip install -r requirements.txt
python app.py
```

Visit **http://127.0.0.1:5000** — you'll land on the sign-in page.

**Demo login:**
- Email: `demo@wavetunes.app`
- Password: `password123`

Or just create a new account from the Sign Up tab.

---

## Deploying to Render

This repo is already configured for Render:

1. Push the repo to GitHub (root of the repo must contain `app.py`, `requirements.txt`, and `Procfile`)
2. On Render: **New → Web Service** → connect the repo
3. **Build Command:**
   ```
   pip install -r requirements.txt
   ```
4. **Start Command:**
   ```
   gunicorn app:app
   ```
5. Add an environment variable:
   - `SECRET_KEY` → any random string
6. Deploy 🎉

(Alternatively, use **New → Blueprint** and Render will pick up `render.yaml` automatically.)

---

## Known Limitations

This project is currently a **frontend + UX prototype** with a working Flask backend for routing, auth, and forms — but a few things are intentionally simplified for now:

- **No database.** Users, likes, and playlists are stored in an in-memory Python dict (`USERS` in `app.py`). This means **all data resets whenever the app restarts or redeploys.** Swapping this for Postgres (e.g. via SQLAlchemy) is the natural next step.
- **No real audio.** The mini player generates a short demo tone per track via the Web Audio API instead of streaming actual `.mp3` files — there's no audio storage/streaming layer yet.
- **Ephemeral file storage.** Profile picture uploads are saved to `static/images/avatars/` on disk, which is wiped on every Render redeploy. A persistent store (S3, Cloudinary, etc.) would be needed for production use.

## Roadmap

- [ ] Postgres database for users, playlists, and likes
- [ ] Real audio file storage + streaming (byte-range requests for seeking)
- [ ] Persistent storage for uploaded avatars (S3 / Cloudinary)
- [ ] Password reset via email
- [ ] Deployed, shareable playlists

---

## License

This project is for personal/portfolio use.
