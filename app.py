"""
Dynamic portfolio site for Laura Mulati, with an admin panel to manage it.

Run:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:5000  (public site)
     and http://127.0.0.1:5000/admin  (admin panel)

First-run admin login: admin / ChangeMe!123 — change it immediately from
Admin > Change Password.
"""
import secrets
from functools import wraps

from flask import (Flask, abort, flash, jsonify, redirect, render_template,
                    request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

import datastore as ds

app = Flask(__name__)
app.secret_key = ds.get_secret_key()
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")

COLLECTIONS = {
    "experience": "experience",
    "projects": "projects",
    "competencies": "competencies",
    "skills": "skills",
    "education": "education",
    "certifications": "certifications",
    "references": "references",
}
REORDERABLE = {"projects", "competencies", "skills"}


# ---------------------------------------------------------------- helpers --
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def csrf_token() -> str:
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_hex(16)
    return session["_csrf"]


app.jinja_env.globals["csrf_token"] = csrf_token


def validate_csrf():
    token = request.form.get("_csrf")
    if not token or not secrets.compare_digest(token, session.get("_csrf", "")):
        abort(400, "Invalid or expired form submission. Please try again.")


def find_by_id(rows, item_id):
    return next((r for r in rows if r.get("id") == item_id), None)


def lines(text):
    return [line.strip() for line in (text or "").splitlines() if line.strip()]


# ------------------------------------------------------------ public site --
@app.route("/")
def index():
    content = ds.get_content()
    return render_template(
        "index.html",
        profile=content["profile"],
        experience=ds.enrich_experience(content),
        projects=ds.enrich_projects(content),
        competencies=content["competencies"],
        skills=content["skills"],
        education=ds.enrich_education(content),
        certifications=ds.enrich_certifications(content),
        references=content["references"],
        stats=ds.build_stats(content),
        tags=ds.tags_dict(content),
    )


@app.route("/api/experience")
def api_experience():
    tag = request.args.get("tag", "all")
    content = ds.get_content()
    rows = ds.enrich_experience(content)
    if tag != "all":
        rows = [r for r in rows if tag in r["tags"]]
    return jsonify(rows)


@app.route("/api/projects")
def api_projects():
    tag = request.args.get("tag", "all")
    content = ds.get_content()
    rows = ds.enrich_projects(content)
    if tag != "all":
        rows = [r for r in rows if tag in r["tags"]]
    return jsonify(rows)


@app.route("/api/skills")
def api_skills():
    group = request.args.get("group", "all")
    rows = ds.get_content()["skills"]
    if group != "all":
        rows = [r for r in rows if r["group"] == group]
    return jsonify(rows)


@app.route("/api/stats")
def api_stats():
    return jsonify(ds.build_stats(ds.get_content()))


# ----------------------------------------------------------------- admin --
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin"):
        return redirect(url_for("admin_dashboard"))
    if request.method == "POST":
        validate_csrf()
        auth = ds.get_content()["auth"]
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == auth["username"] and check_password_hash(auth["password_hash"], password):
            session.clear()
            session["admin"] = True
            session["_csrf"] = secrets.token_hex(16)
            flash("Welcome back, Laura.", "success")
            return redirect(request.args.get("next") or url_for("admin_dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("admin/login.html")


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.route("/admin")
@login_required
def admin_dashboard():
    content = ds.get_content()
    return render_template("admin/dashboard.html", content=content, stats=ds.build_stats(content))


@app.route("/admin/profile", methods=["GET", "POST"])
@login_required
def admin_profile():
    content = ds.get_content()
    if request.method == "POST":
        validate_csrf()
        content["profile"] = {
            "name": request.form.get("name", "").strip(),
            "title": request.form.get("title", "").strip(),
            "location": request.form.get("location", "").strip(),
            "email": request.form.get("email", "").strip(),
            "phones": lines(request.form.get("phones")),
            "linkedin": request.form.get("linkedin", "").strip(),
            "linkedin_display": request.form.get("linkedin_display", "").strip(),
            "summary": request.form.get("summary", "").strip(),
        }
        ds.save_content(content)
        flash("Profile updated.", "success")
        return redirect(url_for("admin_profile"))
    return render_template("admin/profile_form.html", profile=content["profile"])


@app.route("/admin/password", methods=["GET", "POST"])
@login_required
def admin_password():
    if request.method == "POST":
        validate_csrf()
        content = ds.get_content()
        current = request.form.get("current", "")
        new = request.form.get("new", "")
        confirm = request.form.get("confirm", "")
        if not check_password_hash(content["auth"]["password_hash"], current):
            flash("Current password is incorrect.", "error")
        elif len(new) < 8:
            flash("New password must be at least 8 characters.", "error")
        elif new != confirm:
            flash("New password and confirmation do not match.", "error")
        else:
            content["auth"]["password_hash"] = generate_password_hash(new)
            ds.save_content(content)
            flash("Password updated.", "success")
            return redirect(url_for("admin_dashboard"))
    return render_template("admin/password_form.html")


@app.route("/admin/<entity>/<item_id>/delete", methods=["POST"])
@login_required
def admin_delete(entity, item_id):
    if entity not in COLLECTIONS:
        abort(404)
    validate_csrf()
    content = ds.get_content()
    key = COLLECTIONS[entity]
    content[key] = [row for row in content[key] if row.get("id") != item_id]
    ds.save_content(content)
    flash("Deleted.", "success")
    return redirect(request.referrer or url_for("admin_dashboard"))


@app.route("/admin/<entity>/<item_id>/move/<direction>", methods=["POST"])
@login_required
def admin_move(entity, item_id, direction):
    if entity not in REORDERABLE or direction not in ("up", "down"):
        abort(404)
    validate_csrf()
    content = ds.get_content()
    key = COLLECTIONS[entity]
    rows = content[key]
    idx = next((i for i, r in enumerate(rows) if r.get("id") == item_id), None)
    if idx is None:
        abort(404)
    swap_idx = idx - 1 if direction == "up" else idx + 1
    if 0 <= swap_idx < len(rows):
        rows[idx], rows[swap_idx] = rows[swap_idx], rows[idx]
        ds.save_content(content)
    return redirect(request.referrer or url_for("admin_dashboard"))


# -- Experience --
def _experience_from_form(form, tag_keys):
    highlights = []
    for line in lines(form.get("highlights")):
        title, _, desc = line.partition("|")
        highlights.append({"title": title.strip(), "desc": desc.strip()})
    return {
        "role": form.get("role", "").strip(),
        "org": form.get("org", "").strip(),
        "location": form.get("location", "").strip(),
        "start": form.get("start") or None,
        "end": form.get("end") or None,
        "tags": [t for t in form.getlist("tags") if t in tag_keys],
        "highlights": highlights,
    }


@app.route("/admin/experience")
@login_required
def admin_experience_list():
    content = ds.get_content()
    return render_template("admin/experience_list.html", rows=ds.enrich_experience(content))


@app.route("/admin/experience/new", methods=["GET", "POST"])
@login_required
def admin_experience_new():
    content = ds.get_content()
    if request.method == "POST":
        validate_csrf()
        item = _experience_from_form(request.form, ds.tags_dict(content))
        item["id"] = ds.new_id()
        content["experience"].append(item)
        ds.save_content(content)
        flash("Role added.", "success")
        return redirect(url_for("admin_experience_list"))
    return render_template("admin/experience_form.html", item=None, tags=content["tags"])


@app.route("/admin/experience/<item_id>/edit", methods=["GET", "POST"])
@login_required
def admin_experience_edit(item_id):
    content = ds.get_content()
    item = find_by_id(content["experience"], item_id)
    if not item:
        abort(404)
    if request.method == "POST":
        validate_csrf()
        updated = _experience_from_form(request.form, ds.tags_dict(content))
        updated["id"] = item_id
        content["experience"] = [updated if r["id"] == item_id else r for r in content["experience"]]
        ds.save_content(content)
        flash("Role updated.", "success")
        return redirect(url_for("admin_experience_list"))
    highlights_text = "\n".join(f"{h['title']} | {h['desc']}" for h in item["highlights"])
    return render_template("admin/experience_form.html", item=item, tags=content["tags"], highlights_text=highlights_text)


# -- Projects --
@app.route("/admin/projects")
@login_required
def admin_projects_list():
    return render_template("admin/projects_list.html", rows=ds.enrich_projects(ds.get_content()))


def _project_from_form(form, tag_keys):
    links = []
    for line in lines(form.get("links")):
        label, _, url = line.partition("|")
        url = url.strip()
        if url:
            links.append({"label": label.strip() or url, "url": url})
    return {
        "title": form.get("title", "").strip(),
        "org": form.get("org", "").strip(),
        "period": form.get("period", "").strip(),
        "summary": form.get("summary", "").strip(),
        "tags": [t for t in form.getlist("tags") if t in tag_keys],
        "links": links,
    }


@app.route("/admin/projects/new", methods=["GET", "POST"])
@login_required
def admin_projects_new():
    content = ds.get_content()
    if request.method == "POST":
        validate_csrf()
        item = _project_from_form(request.form, ds.tags_dict(content))
        item["id"] = ds.new_id()
        content["projects"].append(item)
        ds.save_content(content)
        flash("Project added.", "success")
        return redirect(url_for("admin_projects_list"))
    return render_template("admin/project_form.html", item=None, tags=content["tags"])


@app.route("/admin/projects/<item_id>/edit", methods=["GET", "POST"])
@login_required
def admin_projects_edit(item_id):
    content = ds.get_content()
    item = find_by_id(content["projects"], item_id)
    if not item:
        abort(404)
    if request.method == "POST":
        validate_csrf()
        updated = _project_from_form(request.form, ds.tags_dict(content))
        updated["id"] = item_id
        content["projects"] = [updated if r["id"] == item_id else r for r in content["projects"]]
        ds.save_content(content)
        flash("Project updated.", "success")
        return redirect(url_for("admin_projects_list"))
    links_text = "\n".join(f"{l['label']} | {l['url']}" for l in item["links"])
    return render_template("admin/project_form.html", item=item, tags=content["tags"], links_text=links_text)


# -- Competencies --
@app.route("/admin/competencies")
@login_required
def admin_competencies_list():
    return render_template("admin/competencies_list.html", rows=ds.get_content()["competencies"])


def _competency_from_form(form):
    return {
        "category": form.get("category", "").strip(),
        "icon": form.get("icon") if form.get("icon") in ds.ICON_CHOICES else "sparkles",
        "items": lines(form.get("items")),
    }


@app.route("/admin/competencies/new", methods=["GET", "POST"])
@login_required
def admin_competencies_new():
    content = ds.get_content()
    if request.method == "POST":
        validate_csrf()
        item = _competency_from_form(request.form)
        item["id"] = ds.new_id()
        content["competencies"].append(item)
        ds.save_content(content)
        flash("Competency added.", "success")
        return redirect(url_for("admin_competencies_list"))
    return render_template("admin/competency_form.html", item=None, icons=ds.ICON_CHOICES)


@app.route("/admin/competencies/<item_id>/edit", methods=["GET", "POST"])
@login_required
def admin_competencies_edit(item_id):
    content = ds.get_content()
    item = find_by_id(content["competencies"], item_id)
    if not item:
        abort(404)
    if request.method == "POST":
        validate_csrf()
        updated = _competency_from_form(request.form)
        updated["id"] = item_id
        content["competencies"] = [updated if r["id"] == item_id else r for r in content["competencies"]]
        ds.save_content(content)
        flash("Competency updated.", "success")
        return redirect(url_for("admin_competencies_list"))
    items_text = "\n".join(item["items"])
    return render_template("admin/competency_form.html", item=item, icons=ds.ICON_CHOICES, items_text=items_text)


# -- Skills --
@app.route("/admin/skills")
@login_required
def admin_skills_list():
    return render_template("admin/skills_list.html", rows=ds.get_content()["skills"])


def _skill_from_form(form):
    try:
        level = int(form.get("level", 0))
    except ValueError:
        level = 0
    return {
        "name": form.get("name", "").strip(),
        "level": max(0, min(100, level)),
        "group": form.get("group", "communications"),
    }


@app.route("/admin/skills/new", methods=["GET", "POST"])
@login_required
def admin_skills_new():
    content = ds.get_content()
    if request.method == "POST":
        validate_csrf()
        item = _skill_from_form(request.form)
        item["id"] = ds.new_id()
        content["skills"].append(item)
        ds.save_content(content)
        flash("Skill added.", "success")
        return redirect(url_for("admin_skills_list"))
    return render_template("admin/skill_form.html", item=None, tags=content["tags"])


@app.route("/admin/skills/<item_id>/edit", methods=["GET", "POST"])
@login_required
def admin_skills_edit(item_id):
    content = ds.get_content()
    item = find_by_id(content["skills"], item_id)
    if not item:
        abort(404)
    if request.method == "POST":
        validate_csrf()
        updated = _skill_from_form(request.form)
        updated["id"] = item_id
        content["skills"] = [updated if r["id"] == item_id else r for r in content["skills"]]
        ds.save_content(content)
        flash("Skill updated.", "success")
        return redirect(url_for("admin_skills_list"))
    return render_template("admin/skill_form.html", item=item, tags=content["tags"])


# -- Education --
@app.route("/admin/education")
@login_required
def admin_education_list():
    return render_template("admin/education_list.html", rows=ds.get_content()["education"])


def _education_from_form(form):
    return {
        "degree": form.get("degree", "").strip(),
        "school": form.get("school", "").strip(),
        "start": form.get("start") or None,
        "end": form.get("end") or None,
        "detail": form.get("detail", "").strip(),
    }


@app.route("/admin/education/new", methods=["GET", "POST"])
@login_required
def admin_education_new():
    content = ds.get_content()
    if request.method == "POST":
        validate_csrf()
        item = _education_from_form(request.form)
        item["id"] = ds.new_id()
        content["education"].append(item)
        ds.save_content(content)
        flash("Education entry added.", "success")
        return redirect(url_for("admin_education_list"))
    return render_template("admin/education_form.html", item=None)


@app.route("/admin/education/<item_id>/edit", methods=["GET", "POST"])
@login_required
def admin_education_edit(item_id):
    content = ds.get_content()
    item = find_by_id(content["education"], item_id)
    if not item:
        abort(404)
    if request.method == "POST":
        validate_csrf()
        updated = _education_from_form(request.form)
        updated["id"] = item_id
        content["education"] = [updated if r["id"] == item_id else r for r in content["education"]]
        ds.save_content(content)
        flash("Education entry updated.", "success")
        return redirect(url_for("admin_education_list"))
    return render_template("admin/education_form.html", item=item)


# -- Certifications --
@app.route("/admin/certifications")
@login_required
def admin_certifications_list():
    return render_template("admin/certifications_list.html", rows=ds.get_content()["certifications"])


def _certification_from_form(form):
    return {
        "name": form.get("name", "").strip(),
        "issuer": form.get("issuer", "").strip(),
        "date": form.get("date") or None,
        "detail": form.get("detail", "").strip(),
    }


@app.route("/admin/certifications/new", methods=["GET", "POST"])
@login_required
def admin_certifications_new():
    content = ds.get_content()
    if request.method == "POST":
        validate_csrf()
        item = _certification_from_form(request.form)
        item["id"] = ds.new_id()
        content["certifications"].append(item)
        ds.save_content(content)
        flash("Certification added.", "success")
        return redirect(url_for("admin_certifications_list"))
    return render_template("admin/certification_form.html", item=None)


@app.route("/admin/certifications/<item_id>/edit", methods=["GET", "POST"])
@login_required
def admin_certifications_edit(item_id):
    content = ds.get_content()
    item = find_by_id(content["certifications"], item_id)
    if not item:
        abort(404)
    if request.method == "POST":
        validate_csrf()
        updated = _certification_from_form(request.form)
        updated["id"] = item_id
        content["certifications"] = [updated if r["id"] == item_id else r for r in content["certifications"]]
        ds.save_content(content)
        flash("Certification updated.", "success")
        return redirect(url_for("admin_certifications_list"))
    return render_template("admin/certification_form.html", item=item)


# -- References --
@app.route("/admin/references")
@login_required
def admin_references_list():
    return render_template("admin/references_list.html", rows=ds.get_content()["references"])


def _reference_from_form(form):
    return {
        "name": form.get("name", "").strip(),
        "title": form.get("title", "").strip(),
        "org": form.get("org", "").strip(),
    }


@app.route("/admin/references/new", methods=["GET", "POST"])
@login_required
def admin_references_new():
    content = ds.get_content()
    if request.method == "POST":
        validate_csrf()
        item = _reference_from_form(request.form)
        item["id"] = ds.new_id()
        content["references"].append(item)
        ds.save_content(content)
        flash("Reference added.", "success")
        return redirect(url_for("admin_references_list"))
    return render_template("admin/reference_form.html", item=None)


@app.route("/admin/references/<item_id>/edit", methods=["GET", "POST"])
@login_required
def admin_references_edit(item_id):
    content = ds.get_content()
    item = find_by_id(content["references"], item_id)
    if not item:
        abort(404)
    if request.method == "POST":
        validate_csrf()
        updated = _reference_from_form(request.form)
        updated["id"] = item_id
        content["references"] = [updated if r["id"] == item_id else r for r in content["references"]]
        ds.save_content(content)
        flash("Reference updated.", "success")
        return redirect(url_for("admin_references_list"))
    return render_template("admin/reference_form.html", item=item)


if __name__ == "__main__":
    app.run(debug=True)
