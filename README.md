# Laura Mulati — Portfolio

A dynamic portfolio site for Laura Mulati (Communications | Knowledge
Management | Program Development Specialist), with a built-in admin panel to
manage every piece of content — no code edits required.

The project ships as **two interchangeable apps that share the same content
store** (`content.json`, via [datastore.py](datastore.py)):

| App | Best for | Entry point |
|---|---|---|
| **Streamlit** | Deploying on Streamlit Community Cloud | `streamlit_app.py` |
| **Flask** | Local use with a richer, route-based admin UI | `app.py` |

Edit content in either one and the change shows up in both, since they read
and write the same `content.json`.

## Features

**Public site**
- Hero, stats, and About sections built from live data (years of experience,
  organizations, etc. are computed, not hardcoded)
- Filterable experience timeline and projects grid (filter by focus area)
- Projects & Resources section with links out to the organizations/programs worked with
- Skills bars, education & certifications, contact section
- Light, bluish-white theme; inline SVG icon set (no external assets)

**Admin panel**
- Login-gated, hashed password (Werkzeug)
- Full CRUD for Profile, Experience, Projects, Competencies, Skills, Education,
  Certifications, and References
- Manual reordering (move up/down) for Projects, Competencies, and Skills
- Change-password page

## Getting started — Streamlit (recommended for deployment)

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Opens at http://localhost:8501 — the sidebar switches between **Portfolio**
(public site) and **Admin**.

### Deploying to Streamlit Community Cloud

1. Push this repo to GitHub (already set up)
2. On [share.streamlit.io](https://share.streamlit.io), create a new app pointing at this repo
3. Set the **main file path** to `streamlit_app.py`
4. Deploy — `requirements.txt` and `.streamlit/config.toml` (the bluish theme) are picked up automatically

`content.json` and `.secret_key` are generated on first run and are **not**
committed to version control — on Streamlit Cloud this means content resets
to the seed data on every redeploy unless you persist it yourself (e.g. via
Streamlit's secrets/external storage). For anything beyond a demo, consider
wiring `datastore.py` to a small external store (Cloud storage bucket,
Google Sheet, tiny hosted DB) instead of the local JSON file.

## Getting started — Flask (local admin alternative)

```bash
pip install -r requirements.txt
python app.py
```

- **Public site:** http://127.0.0.1:5000
- **Admin panel:** http://127.0.0.1:5000/admin

This version isn't deployable on Streamlit Cloud (it runs its own Werkzeug
server, which Streamlit Cloud doesn't proxy) — use it for local editing, or
deploy it separately on a Flask-friendly host (Render, Railway, Fly.io, etc.)
if you'd rather have the route-based admin UI in production.

### First admin login (both apps)

| Field    | Value          |
|----------|----------------|
| Username | `admin`        |
| Password | `ChangeMe!123` |

**Change this immediately** from Admin → Change Password. The password is
stored as a hash (Werkzeug), never in plain text.

## Project structure

```
streamlit_app.py            Streamlit app: public site + admin panel (deployable on Streamlit Cloud)
.streamlit/config.toml      Streamlit theme (bluish-white)
app.py                      Flask routes: public site + admin panel (local alternative)
datastore.py                 Shared content store (load/save content.json, seed defaults, computed stats)
templates/index.html         Flask public site
templates/admin/             Flask admin panel pages
static/css/style.css         Flask public site styles
static/css/admin.css         Flask admin panel styles
static/js/main.js            Flask public site interactivity (filtering, theming, animations)
content.json                  Generated on first run — not committed
.secret_key                   Generated on first run — not committed (Flask session signing key)
```

## Security notes

- `.secret_key` signs Flask session cookies — keep it out of version control (already gitignored)
- `content.json` holds the admin password hash — also gitignored, since it's runtime data, not source
- Flask's built-in server is for local use; don't expose it to the internet as-is if you deploy it directly
