"""
Streamlit portfolio + admin panel for Laura Mulati.

Deployable as-is on Streamlit Community Cloud:
    streamlit run streamlit_app.py

Content lives in content.json (see datastore.py) — the same store used by
the Flask version of this app, so either can be run locally against the
same data.
"""
from datetime import date, datetime

import streamlit as st
from werkzeug.security import check_password_hash, generate_password_hash

import datastore as ds

st.set_page_config(
    page_title="Laura Mulati — Portfolio",
    page_icon="📣",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================== chrome ==

ICON_PATHS = {
    "megaphone": '<path d="M3 10.5v3a1.5 1.5 0 0 0 1.5 1.5H6l5 4V5L6 9H4.5A1.5 1.5 0 0 0 3 10.5Z"/><path d="M15 9a3.2 3.2 0 0 1 0 6"/><path d="M18 6.5a6.6 6.6 0 0 1 0 11"/>',
    "chat": '<rect x="3" y="5" width="18" height="12" rx="3"/><path d="M8 21l3-4"/><circle cx="8.5" cy="11" r="1"/><circle cx="12" cy="11" r="1"/><circle cx="15.5" cy="11" r="1"/>',
    "users": '<circle cx="9" cy="8" r="3.2"/><path d="M3.5 20c0-3.3 2.5-6 5.5-6s5.5 2.7 5.5 6"/><circle cx="17.2" cy="9" r="2.4"/><path d="M15 14.3c2.4.3 4.5 2.2 4.5 5.7"/>',
    "shield-check": '<path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6l7-3Z"/><path d="M9 12l2 2 4-4.5"/>',
    "briefcase": '<rect x="3" y="8" width="18" height="11" rx="2"/><path d="M8 8V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M3 13h18"/>',
    "book-open": '<path d="M3 6.2c3-1.6 6-1.6 9 0v13c-3-1.6-6-1.6-9 0V6.2Z"/><path d="M21 6.2c-3-1.6-6-1.6-9 0v13c3-1.6 6-1.6 9 0V6.2Z"/>',
    "camera": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7l1.4-2.5h5.2L16 7"/><circle cx="12" cy="13.5" r="3.4"/>',
    "heart": '<path d="M12 20.5s-7.2-4.4-9.6-9A5.4 5.4 0 0 1 12 6a5.4 5.4 0 0 1 9.6 5.5c-2.4 4.6-9.6 9-9.6 9Z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "phone": '<path d="M6.5 3.5h3.2l1.3 3.7-2 1.7c1 2.3 2.8 4.1 5.1 5.1l1.7-2 3.7 1.3v3.2a1.7 1.7 0 0 1-1.9 1.7C10.4 17.8 6.2 13.6 5.8 6.4a1.7 1.7 0 0 1 1.7-1.9Z"/>',
    "map-pin": '<path d="M12 21s7-6.7 7-11.5A7 7 0 0 0 5 9.5C5 14.3 12 21 12 21Z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "graduation-cap": '<path d="M12 3.5 22 8l-10 4.5L2 8l10-4.5Z"/><path d="M6.5 10.5V15c0 1.6 2.7 3 5.5 3s5.5-1.4 5.5-3v-4.5"/><path d="M22 8v6"/>',
    "award": '<circle cx="12" cy="8.5" r="5"/><path d="M8.7 13 7 20.5l5-3 5 3-1.7-7.5"/>',
    "network": '<circle cx="6" cy="6" r="2.1"/><circle cx="18" cy="6" r="2.1"/><circle cx="12" cy="18" r="2.1"/><path d="M7.7 7.2 11 16.3M16.3 7.2 13 16.3M8.3 6h7.4"/>',
    "sparkles": '<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9L12 3Z"/><path d="M19 14.5l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8.8-2Z"/>',
    "external": '<path d="M14 4h6v6"/><path d="M20 4 10 14"/><path d="M18 14v4a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4"/>',
    "lock": '<rect x="4" y="10" width="16" height="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
}


def icon(name: str, cls: str = "icon") -> str:
    path = ICON_PATHS.get(name, "")
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{path}</svg>'


CUSTOM_CSS = """
<style>
:root {
  --bg: #f3f7fe; --bg-alt: #e8f0fc; --surface: #ffffff; --border: #d7e3f7;
  --text: #0f1e3a; --text-muted: #526080; --accent: #2563eb; --accent-2: #38bdf8;
  --accent-soft: #e2edfd; --shadow: 0 10px 30px -12px rgba(37,99,235,.2); --radius: 16px;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0a1220; --bg-alt: #0e1830; --surface: #121e38; --border: #223255;
    --text: #eef4ff; --text-muted: #9fb1d6; --accent: #60a5fa; --accent-2: #38bdf8;
    --accent-soft: rgba(96,165,250,.16); --shadow: 0 10px 30px -12px rgba(0,0,0,.6);
  }
}
.icon { width: 20px; height: 20px; flex: none; fill: none; stroke: currentColor; stroke-width: 1.7; stroke-linecap: round; stroke-linejoin: round; vertical-align: -4px; }
.eyebrow-icon { width: 15px; height: 15px; margin-right: 6px; }
.meta-icon { width: 13px; height: 13px; margin-right: 4px; }
.contact-icon { width: 17px; height: 17px; margin-right: 8px; color: var(--accent); }
.link-icon { width: 14px; height: 14px; margin-right: 6px; color: var(--accent); }

.hero { position: relative; padding: 40px 20px 70px; text-align: center; border-radius: var(--radius); overflow: hidden;
  background: radial-gradient(circle at 22% 20%, var(--accent-soft), transparent 55%),
              radial-gradient(circle at 82% 25%, color-mix(in srgb, var(--accent-2) 22%, transparent), transparent 55%); }
.hero-inner { position: relative; z-index: 1; max-width: 720px; margin: 0 auto; }
.eyebrow { display: flex; align-items: center; justify-content: center; text-transform: uppercase; letter-spacing: .12em; font-size: .78rem; color: var(--accent); font-weight: 700; margin-bottom: 6px; }
.hero h1 { font-size: clamp(2rem, 4.4vw, 3rem); font-weight: 800; margin: 0 0 6px; color: var(--text); }
.hero-title { font-size: clamp(1rem, 2vw, 1.2rem); color: var(--text-muted); font-weight: 600; margin-bottom: 1rem; }
.hero-summary { color: var(--text-muted); font-size: 1rem; max-width: 620px; margin: 0 auto; }
.hero-badge { position: absolute; width: 52px; height: 52px; border-radius: 16px; background: var(--surface); border: 1px solid var(--border);
  box-shadow: var(--shadow); display: flex; align-items: center; justify-content: center; color: var(--accent); animation: float 5.5s ease-in-out infinite; }
.hero-badge .icon { width: 22px; height: 22px; }
.badge-1 { top: 8%; left: 6%; animation-delay: 0s; } .badge-2 { top: 12%; right: 7%; animation-delay: .7s; }
.badge-3 { bottom: 10%; left: 10%; animation-delay: 1.4s; } .badge-4 { bottom: 6%; right: 11%; animation-delay: 2.1s; }
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-12px); } }
@media (max-width: 900px) { .hero-badge { display: none; } }

.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px,1fr)); gap: 16px; margin: 24px 0; }
.stat-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 22px 16px; text-align: center; box-shadow: var(--shadow); }
.stat-icon { display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; width: 40px; height: 40px; border-radius: 12px; background: var(--accent-soft); color: var(--accent); }
.stat-number { display: block; font-size: 1.9rem; font-weight: 800; color: var(--accent); }
.stat-label { color: var(--text-muted); font-size: .85rem; font-weight: 500; }

.section-head { margin: 30px 0 18px; }
.section-eyebrow { display: flex; align-items: center; text-transform: uppercase; letter-spacing: .12em; font-size: .76rem; color: var(--accent); font-weight: 700; margin-bottom: 4px; }
.section-head h2 { font-size: 1.5rem; margin: 0; color: var(--text); }

.competency-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px,1fr)); gap: 16px; }
.competency-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; box-shadow: var(--shadow); }
.card-icon { display: flex; align-items: center; justify-content: center; margin-bottom: 12px; width: 40px; height: 40px; border-radius: 12px; background: linear-gradient(135deg, var(--accent-soft), transparent); color: var(--accent); }
.competency-card h3 { font-size: 1rem; color: var(--accent); margin: 0 0 10px; }
.competency-card ul { margin: 0; padding: 0; list-style: none; }
.competency-card li { padding: 4px 0 4px 16px; position: relative; color: var(--text-muted); font-size: .9rem; }
.competency-card li::before { content: ""; position: absolute; left: 0; top: 12px; width: 6px; height: 6px; border-radius: 50%; background: var(--accent-2); }

.timeline { position: relative; padding-left: 24px; }
.timeline::before { content: ""; position: absolute; left: 5px; top: 6px; bottom: 6px; width: 2px; background: linear-gradient(var(--accent), var(--accent-2)); opacity: .45; }
.timeline-item { position: relative; margin-bottom: 18px; }
.timeline-dot { position: absolute; left: -24px; top: 20px; width: 12px; height: 12px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 0 4px var(--accent-soft); }
.timeline-card, .project-card, .edu-card, .contact-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px 22px; box-shadow: var(--shadow); }
.timeline-card-head, .project-card-head { display: flex; justify-content: space-between; gap: 14px; flex-wrap: wrap; margin-bottom: 8px; }
.timeline-card h3, .project-card h3 { font-size: 1.05rem; margin: 0 0 2px; color: var(--text); }
.org { color: var(--accent); font-weight: 600; font-size: .88rem; margin: 0; }
.timeline-meta { text-align: right; font-size: .8rem; color: var(--text-muted); display: flex; flex-direction: column; gap: 2px; }
.timeline-meta .loc { display: inline-flex; align-items: center; justify-content: flex-end; }
.tag-chips { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }
.chip { background: var(--accent-soft); color: var(--accent); font-size: .72rem; font-weight: 700; padding: 3px 9px; border-radius: 999px; text-transform: uppercase; letter-spacing: .03em; }
.highlights { margin: 0; padding: 0; list-style: none; }
.highlights li { font-size: .9rem; color: var(--text-muted); padding: 3px 0; }
.highlights strong { color: var(--text); }

.project-grid, .edu-grid, .contact-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px,1fr)); gap: 16px; }
.project-card { display: flex; flex-direction: column; }
.project-period { font-size: .76rem; color: var(--text-muted); white-space: nowrap; }
.project-summary { color: var(--text-muted); font-size: .88rem; margin: 8px 0 12px; flex: 1; }
.project-links { display: flex; flex-wrap: wrap; gap: 8px 16px; padding-top: 10px; border-top: 1px solid var(--border); }
.project-links a { display: inline-flex; align-items: center; font-size: .84rem; font-weight: 600; color: var(--accent); text-decoration: none; }
.project-links a:hover { text-decoration: underline; }

.edu-kind { display: inline-flex; align-items: center; font-size: .7rem; text-transform: uppercase; letter-spacing: .07em; color: var(--accent-2); font-weight: 700; }
.edu-card h3 { margin: 6px 0 2px; font-size: 1rem; color: var(--text); }
.edu-detail { color: var(--text-muted); font-size: .86rem; margin-top: 6px; }
.date-range { color: var(--text-muted); font-size: .82rem; }

.contact-card h3 { color: var(--accent); font-size: .95rem; margin: 0 0 10px; }
.contact-line { display: flex; align-items: center; font-size: .92rem; color: var(--text); margin: 6px 0; }
.contact-line a { color: var(--text); text-decoration: none; }
.contact-line a:hover { color: var(--accent); }
.reference-item { display: flex; align-items: flex-start; gap: 8px; padding: 6px 0; font-size: .88rem; color: var(--text-muted); }
.reference-item strong { color: var(--text); }

/* CSS-only "grow in" animation for skill bars: only the 0% keyframe is
   defined, so browsers use the element's own inline width as the implicit
   end state — no JS needed to trigger it. */
.skill-track { height: 8px; background: var(--bg-alt); border-radius: 999px; overflow: hidden; border: 1px solid var(--border); margin-top: 6px; }
.skill-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--accent), var(--accent-2)); animation: growBar 1s ease-out; }
@keyframes growBar { from { width: 0; } }
.skill-label { display: flex; justify-content: space-between; font-size: .88rem; color: var(--text); margin-top: 10px; }
.skill-value { color: var(--accent); font-weight: 700; }
</style>
"""


def inject_chrome():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================ public site ==

def render_hero(profile: dict):
    badges = ["megaphone", "chat", "network", "camera"]
    badges_html = "".join(f'<div class="hero-badge badge-{i + 1}">{icon(b)}</div>' for i, b in enumerate(badges))
    st.markdown(
        f"""
        <div class="hero">
          {badges_html}
          <div class="hero-inner">
            <p class="eyebrow">{icon('map-pin', 'icon eyebrow-icon')}{profile['location']}</p>
            <h1>{profile['name']}</h1>
            <p class="hero-title">{profile['title']}</p>
            <p class="hero-summary">{profile['summary']}</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stats(stats: dict):
    cards = [
        ("award", stats["years_experience"], "Years of Experience"),
        ("briefcase", stats["organizations"], "Organizations"),
        ("network", stats["roles_held"], "Roles Held"),
        ("sparkles", stats["competency_areas"], "Core Competency Areas"),
    ]
    cards_html = "".join(
        f'<div class="stat-card"><span class="stat-icon">{icon(i)}</span>'
        f'<span class="stat-number">{v}</span><span class="stat-label">{l}</span></div>'
        for i, v, l in cards
    )
    st.markdown(f'<div class="stats-grid">{cards_html}</div>', unsafe_allow_html=True)


def section_head(icon_name: str, eyebrow: str, title: str):
    st.markdown(
        f"""<div class="section-head">
              <p class="section-eyebrow">{icon(icon_name, 'icon eyebrow-icon')}{eyebrow}</p>
              <h2>{title}</h2>
            </div>""",
        unsafe_allow_html=True,
    )


def render_competencies(competencies: list):
    cards = "".join(
        f'''<div class="competency-card">
              <div class="card-icon">{icon(c["icon"])}</div>
              <h3>{c["category"]}</h3>
              <ul>{"".join(f"<li>{item}</li>" for item in c["items"])}</ul>
            </div>'''
        for c in competencies
    )
    st.markdown(f'<div class="competency-grid">{cards}</div>', unsafe_allow_html=True)


def render_home_tab(content: dict):
    render_hero(content["profile"])
    render_stats(ds.build_stats(content))
    section_head("users", "About", "Core Competencies &amp; Technical Expertise")
    render_competencies(content["competencies"])


def tag_filter_widget(content: dict, key: str) -> str:
    tags = content["tags"]
    labels = {t["key"]: t["label"] for t in tags}
    labels["all"] = "All"
    options = ["all"] + [t["key"] for t in tags]
    selected = st.pills(
        "Filter by focus area", options, default="all",
        format_func=lambda k: labels[k], key=key, label_visibility="collapsed",
    )
    return selected or "all"


def render_experience_tab(content: dict):
    section_head("briefcase", "Career Journey", "Professional Experience")
    selected = tag_filter_widget(content, "exp_filter")
    rows = ds.enrich_experience(content)
    if selected != "all":
        rows = [r for r in rows if selected in r["tags"]]
    if not rows:
        st.info("No roles match this filter yet.")
        return
    cards = "".join(
        f'''<div class="timeline-item">
              <div class="timeline-dot"></div>
              <div class="timeline-card">
                <div class="timeline-card-head">
                  <div><h3>{job["role"]}</h3><p class="org">{job["org"]}</p></div>
                  <div class="timeline-meta">
                    <span class="date-range">{job["start_label"]} – {job["end_label"]}</span>
                    <span class="duration">{job["duration_label"]}</span>
                    <span class="loc">{icon('map-pin', 'icon meta-icon')}{job["location"]}</span>
                  </div>
                </div>
                <div class="tag-chips">{"".join(f'<span class="chip">{l}</span>' for l in job["tag_labels"])}</div>
                <ul class="highlights">{"".join(f'<li><strong>{h["title"]}:</strong> {h["desc"]}</li>' for h in job["highlights"])}</ul>
              </div>
            </div>'''
        for job in rows
    )
    st.markdown(f'<div class="timeline">{cards}</div>', unsafe_allow_html=True)


def render_projects_tab(content: dict):
    section_head("network", "Selected Work", "Projects &amp; Resources")
    selected = tag_filter_widget(content, "proj_filter")
    rows = ds.enrich_projects(content)
    if selected != "all":
        rows = [r for r in rows if selected in r["tags"]]
    if not rows:
        st.info("No projects match this filter yet.")
        return
    cards = "".join(
        f'''<div class="project-card">
              <div class="project-card-head">
                <div><h3>{p["title"]}</h3><p class="org">{p["org"]}</p></div>
                <span class="project-period">{p["period"]}</span>
              </div>
              <div class="tag-chips">{"".join(f'<span class="chip">{l}</span>' for l in p["tag_labels"])}</div>
              <p class="project-summary">{p["summary"]}</p>
              {f'<div class="project-links">{"".join(f"<a href={l['url']!r} target=_blank rel=noopener>{icon('external', 'icon link-icon')}{l['label']}</a>" for l in p["links"])}</div>' if p["links"] else ""}
            </div>'''
        for p in rows
    )
    st.markdown(f'<div class="project-grid">{cards}</div>', unsafe_allow_html=True)


def render_skills_tab(content: dict):
    section_head("sparkles", "Capabilities", "Skills &amp; Proficiency")
    selected = tag_filter_widget(content, "skill_filter")
    rows = content["skills"]
    if selected != "all":
        rows = [r for r in rows if r["group"] == selected]
    if not rows:
        st.info("No skills match this filter yet.")
        return
    rows_html = "".join(
        f'''<div class="skill-label"><span>{s["name"]}</span><span class="skill-value">{s["level"]}%</span></div>
            <div class="skill-track"><div class="skill-fill" style="width:{s["level"]}%"></div></div>'''
        for s in rows
    )
    st.markdown(f'<div>{rows_html}</div>', unsafe_allow_html=True)


def render_education_tab(content: dict):
    section_head("graduation-cap", "Foundations", "Education &amp; Certifications")
    education = ds.enrich_education(content)
    certifications = ds.enrich_certifications(content)
    cards = "".join(
        f'''<div class="edu-card">
              <span class="edu-kind">{icon('graduation-cap', 'icon meta-icon')}Education</span>
              <h3>{e["degree"]}</h3><p class="org">{e["school"]}</p>
              <p class="date-range">{e["start_label"]} – {e["end_label"]}</p>
              <p class="edu-detail">{e["detail"]}</p>
            </div>'''
        for e in education
    )
    cards += "".join(
        f'''<div class="edu-card">
              <span class="edu-kind">{icon('award', 'icon meta-icon')}Certification</span>
              <h3>{c["name"]}</h3><p class="org">{c["issuer"]}</p>
              <p class="date-range">{c["date_label"]}</p>
              <p class="edu-detail">{c["detail"]}</p>
            </div>'''
        for c in certifications
    )
    st.markdown(f'<div class="edu-grid">{cards}</div>', unsafe_allow_html=True)


def render_contact_tab(content: dict):
    section_head("chat", "Let's Connect", "Contact")
    profile = content["profile"]
    phones_html = "".join(f'<p class="contact-line">{icon("phone", "icon contact-icon")}{p}</p>' for p in profile["phones"])
    references_html = "".join(
        f'''<div class="reference-item">{icon("users", "icon contact-icon")}
              <span><strong>{r["name"]}</strong> — {r["title"]}, {r["org"]}</span></div>'''
        for r in content["references"]
    )
    st.markdown(
        f"""
        <div class="contact-grid">
          <div class="contact-card">
            <h3>Direct</h3>
            <p class="contact-line">{icon('mail', 'icon contact-icon')}<a href="mailto:{profile['email']}">{profile['email']}</a></p>
            {phones_html}
            <p class="contact-line">{icon('network', 'icon contact-icon')}<a href="{profile['linkedin']}" target="_blank" rel="noopener">{profile['linkedin_display']}</a></p>
            <p class="contact-line">{icon('map-pin', 'icon contact-icon')}{profile['location']}</p>
          </div>
          <div class="contact-card">
            <h3>References</h3>
            {references_html}
            <p style="color:var(--text-muted);font-size:.82rem;margin-top:10px;">Full contact details available upon request.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_portfolio(content: dict):
    inject_chrome()
    tabs = st.tabs(["🏠 Home", "💼 Experience", "🚀 Projects", "⚡ Skills", "🎓 Education", "✉️ Contact"])
    with tabs[0]:
        render_home_tab(content)
    with tabs[1]:
        render_experience_tab(content)
    with tabs[2]:
        render_projects_tab(content)
    with tabs[3]:
        render_skills_tab(content)
    with tabs[4]:
        render_education_tab(content)
    with tabs[5]:
        render_contact_tab(content)


# =================================================================== admin ==

def login_form(content: dict):
    inject_chrome()
    st.markdown(
        f'<div style="max-width:360px;margin:60px auto;text-align:center;">'
        f'<div class="stat-icon" style="width:52px;height:52px;margin:0 auto 14px;">{icon("lock")}</div>'
        f'<h2 style="margin-bottom:4px;">Portfolio Admin</h2>'
        f'<p style="color:var(--text-muted);margin-bottom:20px;">Sign in to manage Laura\'s portfolio content.</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log in", type="primary", width="stretch")
        if submitted:
            auth = content["auth"]
            if username == auth["username"] and check_password_hash(auth["password_hash"], password):
                st.session_state["admin_authed"] = True
                st.rerun()
            else:
                st.error("Invalid username or password.")
        st.caption(
            "First time here? Default login is **admin** / **ChangeMe!123** — "
            "change it right after signing in (Manage → Change Password)."
        )


def lines(text: str) -> list:
    return [line.strip() for line in (text or "").splitlines() if line.strip()]


def manage_profile(content: dict):
    st.subheader("Profile")
    p = content["profile"]
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Full name", p["name"])
        location = col2.text_input("Location", p["location"])
        title = st.text_input("Title", p["title"])
        summary = st.text_area("Summary", p["summary"], height=160)
        col3, col4 = st.columns(2)
        email = col3.text_input("Email", p["email"])
        phones = col4.text_area("Phone numbers (one per line)", "\n".join(p["phones"]), height=80)
        col5, col6 = st.columns(2)
        linkedin = col5.text_input("LinkedIn URL", p["linkedin"])
        linkedin_display = col6.text_input("LinkedIn display text", p["linkedin_display"])
        submitted = st.form_submit_button("Save changes", type="primary")
    if submitted:
        content["profile"] = {
            "name": name.strip(), "title": title.strip(), "location": location.strip(),
            "email": email.strip(), "phones": lines(phones),
            "linkedin": linkedin.strip(), "linkedin_display": linkedin_display.strip(),
            "summary": summary.strip(),
        }
        ds.save_content(content)
        st.success("Profile updated.")


def manage_password(content: dict):
    st.subheader("Change Password")
    with st.form("password_form"):
        current = st.text_input("Current password", type="password")
        new = st.text_input("New password", type="password")
        confirm = st.text_input("Confirm new password", type="password")
        submitted = st.form_submit_button("Update password", type="primary")
    if submitted:
        if not check_password_hash(content["auth"]["password_hash"], current):
            st.error("Current password is incorrect.")
        elif len(new) < 8:
            st.error("New password must be at least 8 characters.")
        elif new != confirm:
            st.error("New password and confirmation do not match.")
        else:
            content["auth"]["password_hash"] = generate_password_hash(new)
            ds.save_content(content)
            st.success("Password updated.")


def reorder_controls(content: dict, key: str, item_id: str, prefix: str):
    rows = content[key]
    idx = next((i for i, r in enumerate(rows) if r["id"] == item_id), None)
    if idx is None:
        return
    c1, c2 = st.columns(2)
    if c1.button("⬆️ Move up", key=f"{prefix}_up_{item_id}", disabled=idx == 0):
        rows[idx - 1], rows[idx] = rows[idx], rows[idx - 1]
        ds.save_content(content)
        st.rerun()
    if c2.button("⬇️ Move down", key=f"{prefix}_down_{item_id}", disabled=idx == len(rows) - 1):
        rows[idx + 1], rows[idx] = rows[idx], rows[idx + 1]
        ds.save_content(content)
        st.rerun()


def manage_experience(content: dict):
    st.subheader("Experience")
    st.caption("Order on the public timeline always follows each role's start date.")
    for job in content["experience"]:
        with st.expander(f"{job['role']} — {job['org']}"):
            _experience_form(content, job)
    with st.expander("➕ Add new role"):
        _experience_form(content, None)


def _experience_form(content: dict, item):
    is_new = item is None
    suffix = item["id"] if item else "new"
    tags_catalog = content["tags"]
    default_tags = item["tags"] if item else []
    default_highlights = item["highlights"] if item else [{"title": "", "desc": ""}]
    default_start = ds._parse_date(item["start"]) if item else date.today()
    default_end = ds._parse_date(item.get("end")) if item else None

    with st.form(f"experience_form_{suffix}"):
        col1, col2 = st.columns(2)
        role = col1.text_input("Role title", item["role"] if item else "")
        org = col2.text_input("Organization", item["org"] if item else "")
        location = st.text_input("Location", item["location"] if item else "")
        col3, col4 = st.columns(2)
        start = col3.date_input("Start date", default_start)
        present = col4.checkbox("Currently working here", value=item is not None and item.get("end") is None)
        end = None if present else col4.date_input("End date", default_end or date.today())
        selected_tags = st.multiselect(
            "Focus areas", [t["key"] for t in tags_catalog],
            default=default_tags, format_func=lambda k: next(t["label"] for t in tags_catalog if t["key"] == k),
        )
        st.caption("Highlights")
        highlights_df = st.data_editor(
            default_highlights, num_rows="dynamic", width="stretch",
            column_config={"title": "Title", "desc": "Description"}, key=f"highlights_{suffix}",
        )
        cols = st.columns([1, 1, 3])
        save_clicked = cols[0].form_submit_button("Add role" if is_new else "Save changes", type="primary")
        delete_clicked = None if is_new else cols[1].form_submit_button("Delete", type="secondary")

    if save_clicked:
        highlights = [
            {"title": (h.get("title") or "").strip(), "desc": (h.get("desc") or "").strip()}
            for h in highlights_df if (h.get("title") or "").strip()
        ]
        payload = {
            "role": role.strip(), "org": org.strip(), "location": location.strip(),
            "start": start.isoformat(), "end": None if present else end.isoformat(),
            "tags": selected_tags, "highlights": highlights,
        }
        if is_new:
            payload["id"] = ds.new_id()
            content["experience"].append(payload)
            st.success("Role added.")
        else:
            payload["id"] = item["id"]
            content["experience"] = [payload if r["id"] == item["id"] else r for r in content["experience"]]
            st.success("Role updated.")
        ds.save_content(content)
        st.rerun()
    if delete_clicked:
        content["experience"] = [r for r in content["experience"] if r["id"] != item["id"]]
        ds.save_content(content)
        st.success("Role deleted.")
        st.rerun()


def manage_projects(content: dict):
    st.subheader("Projects")
    for p in content["projects"]:
        with st.expander(f"{p['title']} — {p['org']}"):
            reorder_controls(content, "projects", p["id"], "proj")
            _project_form(content, p)
    with st.expander("➕ Add new project"):
        _project_form(content, None)


def _project_form(content: dict, item):
    is_new = item is None
    suffix = item["id"] if item else "new"
    tags_catalog = content["tags"]
    default_links = item["links"] if item else [{"label": "", "url": ""}]

    with st.form(f"project_form_{suffix}"):
        title = st.text_input("Project title", item["title"] if item else "")
        col1, col2 = st.columns(2)
        org = col1.text_input("Organization", item["org"] if item else "")
        period = col2.text_input("Period", item["period"] if item else "", placeholder="e.g. 2024 – 2025")
        summary = st.text_area("Summary", item["summary"] if item else "", height=100)
        selected_tags = st.multiselect(
            "Focus areas", [t["key"] for t in tags_catalog],
            default=item["tags"] if item else [], format_func=lambda k: next(t["label"] for t in tags_catalog if t["key"] == k),
        )
        st.caption("Resource links (leave blank if there's nothing public to link to)")
        links_df = st.data_editor(
            default_links, num_rows="dynamic", width="stretch",
            column_config={"label": "Label", "url": "URL"}, key=f"links_{suffix}",
        )
        cols = st.columns([1, 1, 3])
        save_clicked = cols[0].form_submit_button("Add project" if is_new else "Save changes", type="primary")
        delete_clicked = None if is_new else cols[1].form_submit_button("Delete", type="secondary")

    if save_clicked:
        links = [
            {"label": (l.get("label") or "").strip() or (l.get("url") or "").strip(), "url": (l.get("url") or "").strip()}
            for l in links_df if (l.get("url") or "").strip()
        ]
        payload = {
            "title": title.strip(), "org": org.strip(), "period": period.strip(),
            "summary": summary.strip(), "tags": selected_tags, "links": links,
        }
        if is_new:
            payload["id"] = ds.new_id()
            content["projects"].append(payload)
            st.success("Project added.")
        else:
            payload["id"] = item["id"]
            content["projects"] = [payload if r["id"] == item["id"] else r for r in content["projects"]]
            st.success("Project updated.")
        ds.save_content(content)
        st.rerun()
    if delete_clicked:
        content["projects"] = [r for r in content["projects"] if r["id"] != item["id"]]
        ds.save_content(content)
        st.success("Project deleted.")
        st.rerun()


def manage_competencies(content: dict):
    st.subheader("Competencies")
    for c in content["competencies"]:
        with st.expander(f"{c['category']}"):
            reorder_controls(content, "competencies", c["id"], "comp")
            _competency_form(content, c)
    with st.expander("➕ Add new category"):
        _competency_form(content, None)


def _competency_form(content: dict, item):
    is_new = item is None
    suffix = item["id"] if item else "new"
    with st.form(f"competency_form_{suffix}"):
        category = st.text_input("Category name", item["category"] if item else "")
        items_text = st.text_area("Items (one per line)", "\n".join(item["items"]) if item else "", height=120)
        icon_choice = st.selectbox(
            "Icon", ds.ICON_CHOICES,
            index=ds.ICON_CHOICES.index(item["icon"]) if item and item["icon"] in ds.ICON_CHOICES else 0,
        )
        cols = st.columns([1, 1, 3])
        save_clicked = cols[0].form_submit_button("Add category" if is_new else "Save changes", type="primary")
        delete_clicked = None if is_new else cols[1].form_submit_button("Delete", type="secondary")

    if save_clicked:
        payload = {"category": category.strip(), "icon": icon_choice, "items": lines(items_text)}
        if is_new:
            payload["id"] = ds.new_id()
            content["competencies"].append(payload)
            st.success("Category added.")
        else:
            payload["id"] = item["id"]
            content["competencies"] = [payload if r["id"] == item["id"] else r for r in content["competencies"]]
            st.success("Category updated.")
        ds.save_content(content)
        st.rerun()
    if delete_clicked:
        content["competencies"] = [r for r in content["competencies"] if r["id"] != item["id"]]
        ds.save_content(content)
        st.success("Category deleted.")
        st.rerun()


def manage_skills(content: dict):
    st.subheader("Skills")
    for s in content["skills"]:
        with st.expander(f"{s['name']} ({s['level']}%)"):
            reorder_controls(content, "skills", s["id"], "skill")
            _skill_form(content, s)
    with st.expander("➕ Add new skill"):
        _skill_form(content, None)


def _skill_form(content: dict, item):
    is_new = item is None
    suffix = item["id"] if item else "new"
    tags_catalog = content["tags"]
    with st.form(f"skill_form_{suffix}"):
        name = st.text_input("Skill name", item["name"] if item else "")
        col1, col2 = st.columns(2)
        group = col1.selectbox(
            "Group", [t["key"] for t in tags_catalog],
            index=[t["key"] for t in tags_catalog].index(item["group"]) if item else 0,
            format_func=lambda k: next(t["label"] for t in tags_catalog if t["key"] == k),
        )
        level = col2.number_input("Proficiency (0–100)", 0, 100, item["level"] if item else 75)
        cols = st.columns([1, 1, 3])
        save_clicked = cols[0].form_submit_button("Add skill" if is_new else "Save changes", type="primary")
        delete_clicked = None if is_new else cols[1].form_submit_button("Delete", type="secondary")

    if save_clicked:
        payload = {"name": name.strip(), "group": group, "level": int(level)}
        if is_new:
            payload["id"] = ds.new_id()
            content["skills"].append(payload)
            st.success("Skill added.")
        else:
            payload["id"] = item["id"]
            content["skills"] = [payload if r["id"] == item["id"] else r for r in content["skills"]]
            st.success("Skill updated.")
        ds.save_content(content)
        st.rerun()
    if delete_clicked:
        content["skills"] = [r for r in content["skills"] if r["id"] != item["id"]]
        ds.save_content(content)
        st.success("Skill deleted.")
        st.rerun()


def manage_education(content: dict):
    st.subheader("Education")
    for e in content["education"]:
        with st.expander(e["degree"]):
            _education_form(content, e)
    with st.expander("➕ Add new entry"):
        _education_form(content, None)


def _education_form(content: dict, item):
    is_new = item is None
    suffix = item["id"] if item else "new"
    with st.form(f"education_form_{suffix}"):
        degree = st.text_input("Degree / qualification", item["degree"] if item else "")
        school = st.text_input("School", item["school"] if item else "")
        col1, col2 = st.columns(2)
        start = col1.date_input("Start date", ds._parse_date(item["start"]) if item else date.today())
        end = col2.date_input("End date", ds._parse_date(item["end"]) if item else date.today())
        detail = st.text_area("Detail", item["detail"] if item else "", height=100)
        cols = st.columns([1, 1, 3])
        save_clicked = cols[0].form_submit_button("Add entry" if is_new else "Save changes", type="primary")
        delete_clicked = None if is_new else cols[1].form_submit_button("Delete", type="secondary")

    if save_clicked:
        payload = {"degree": degree.strip(), "school": school.strip(), "start": start.isoformat(), "end": end.isoformat(), "detail": detail.strip()}
        if is_new:
            payload["id"] = ds.new_id()
            content["education"].append(payload)
            st.success("Entry added.")
        else:
            payload["id"] = item["id"]
            content["education"] = [payload if r["id"] == item["id"] else r for r in content["education"]]
            st.success("Entry updated.")
        ds.save_content(content)
        st.rerun()
    if delete_clicked:
        content["education"] = [r for r in content["education"] if r["id"] != item["id"]]
        ds.save_content(content)
        st.success("Entry deleted.")
        st.rerun()


def manage_certifications(content: dict):
    st.subheader("Certifications")
    for c in content["certifications"]:
        with st.expander(c["name"]):
            _certification_form(content, c)
    with st.expander("➕ Add new entry"):
        _certification_form(content, None)


def _certification_form(content: dict, item):
    is_new = item is None
    suffix = item["id"] if item else "new"
    with st.form(f"certification_form_{suffix}"):
        name = st.text_input("Certificate name", item["name"] if item else "")
        col1, col2 = st.columns(2)
        issuer = col1.text_input("Issuer", item["issuer"] if item else "")
        cert_date = col2.date_input("Date", ds._parse_date(item["date"]) if item else date.today())
        detail = st.text_area("Detail", item["detail"] if item else "", height=100)
        cols = st.columns([1, 1, 3])
        save_clicked = cols[0].form_submit_button("Add entry" if is_new else "Save changes", type="primary")
        delete_clicked = None if is_new else cols[1].form_submit_button("Delete", type="secondary")

    if save_clicked:
        payload = {"name": name.strip(), "issuer": issuer.strip(), "date": cert_date.isoformat(), "detail": detail.strip()}
        if is_new:
            payload["id"] = ds.new_id()
            content["certifications"].append(payload)
            st.success("Entry added.")
        else:
            payload["id"] = item["id"]
            content["certifications"] = [payload if r["id"] == item["id"] else r for r in content["certifications"]]
            st.success("Entry updated.")
        ds.save_content(content)
        st.rerun()
    if delete_clicked:
        content["certifications"] = [r for r in content["certifications"] if r["id"] != item["id"]]
        ds.save_content(content)
        st.success("Entry deleted.")
        st.rerun()


def manage_references(content: dict):
    st.subheader("References")
    st.caption("Shown on the public Contact tab — phone/email are intentionally kept off the public page.")
    for r in content["references"]:
        with st.expander(r["name"]):
            _reference_form(content, r)
    with st.expander("➕ Add new reference"):
        _reference_form(content, None)


def _reference_form(content: dict, item):
    is_new = item is None
    suffix = item["id"] if item else "new"
    with st.form(f"reference_form_{suffix}"):
        name = st.text_input("Name", item["name"] if item else "")
        title = st.text_input("Title", item["title"] if item else "")
        org = st.text_input("Organization", item["org"] if item else "")
        cols = st.columns([1, 1, 3])
        save_clicked = cols[0].form_submit_button("Add reference" if is_new else "Save changes", type="primary")
        delete_clicked = None if is_new else cols[1].form_submit_button("Delete", type="secondary")

    if save_clicked:
        payload = {"name": name.strip(), "title": title.strip(), "org": org.strip()}
        if is_new:
            payload["id"] = ds.new_id()
            content["references"].append(payload)
            st.success("Reference added.")
        else:
            payload["id"] = item["id"]
            content["references"] = [payload if r["id"] == item["id"] else r for r in content["references"]]
            st.success("Reference updated.")
        ds.save_content(content)
        st.rerun()
    if delete_clicked:
        content["references"] = [r for r in content["references"] if r["id"] != item["id"]]
        ds.save_content(content)
        st.success("Reference deleted.")
        st.rerun()


ADMIN_PAGES = {
    "Profile": manage_profile,
    "Experience": manage_experience,
    "Projects": manage_projects,
    "Competencies": manage_competencies,
    "Skills": manage_skills,
    "Education": manage_education,
    "Certifications": manage_certifications,
    "References": manage_references,
    "Change Password": manage_password,
}


def render_admin(content: dict):
    if not st.session_state.get("admin_authed"):
        login_form(content)
        return
    inject_chrome()
    with st.sidebar:
        st.success("Logged in as admin")
        page = st.radio("Manage", list(ADMIN_PAGES.keys()))
        if st.button("Log out"):
            st.session_state["admin_authed"] = False
            st.rerun()
    ADMIN_PAGES[page](content)


# ==================================================================== main ==

def main():
    content = ds.get_content()
    with st.sidebar:
        st.markdown(f"### {content['profile']['name']}")
        section = st.radio("Navigate", ["Portfolio", "Admin"], label_visibility="collapsed")
    if section == "Portfolio":
        render_portfolio(content)
    else:
        render_admin(content)


main()
