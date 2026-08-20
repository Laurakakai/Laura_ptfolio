"""
JSON-backed content store for the portfolio.

Everything the public site *and* the admin panel read/write lives in
``content.json`` next to this file. On first run the file is seeded from the
DEFAULT content below (the same facts that used to live in data.py, now
editable through the admin panel instead of by hand).
"""
import json
import os
import secrets
import threading
from datetime import date, datetime

from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "content.json")
SECRET_KEY_PATH = os.path.join(BASE_DIR, ".secret_key")

_lock = threading.Lock()

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "ChangeMe!123"

ICON_CHOICES = [
    "megaphone", "chat", "users", "shield-check", "briefcase", "book-open",
    "camera", "heart", "mail", "phone", "map-pin", "graduation-cap",
    "award", "network", "sparkles",
]


def _new_id() -> str:
    return secrets.token_hex(6)


def _default_content() -> dict:
    return {
        "profile": {
            "name": "Laura Mulati",
            "title": "Communications | Knowledge Management | Program Development Specialist",
            "location": "Nairobi, Kenya",
            "email": "lauramulati@gmail.com",
            "phones": ["+254 724 911 684", "+254 703 905 128"],
            "linkedin": "https://www.linkedin.com/in/laura-mulati-a9712a1b7",
            "linkedin_display": "linkedin.com/in/laura-mulati-a9712a1b7",
            "summary": (
                "Results-oriented Communications, Knowledge Management, and Program "
                "Development Specialist with extensive experience delivering high-impact "
                "advocacy, digital marketing, partner due diligence, and information "
                "governance across international non-governmental organizations (INGOs) "
                "and civil society. Proven expertise in multi-channel content creation, "
                "partner engagement, project monitoring, and gender-transformative "
                "programming. Recognized for exceptional organizational acuity, "
                "cross-functional collaboration, and the ability to streamline knowledge "
                "systems in fast-paced environments."
            ),
        },
        "tags": [
            {"key": "programs", "label": "Programs & Grants"},
            {"key": "communications", "label": "Communications & Advocacy"},
            {"key": "digital", "label": "Digital & Content"},
            {"key": "knowledge", "label": "Knowledge Management"},
        ],
        "experience": [
            {
                "id": _new_id(),
                "role": "Program Intern (Access to Finance)",
                "org": "TechnoServe",
                "location": "Mombasa, Kenya",
                "start": "2026-05-11",
                "end": None,
                "tags": ["programs"],
                "highlights": [
                    {"title": "Grant Administration", "desc": "Coordinate application workflows for the Bahari Boost Challenge Fund (BBCF), managing preliminary screening, compliance documentation verification, and applicant communications."},
                    {"title": "Partner Due Diligence", "desc": "Execute due diligence assessments for local partner organizations, synthesizing findings and mapping organizational risk factors."},
                    {"title": "Monitoring & Reporting", "desc": "Review progress reports submitted by partner organizations and grantees, flagging gaps and maintaining structured reporting repositories for donor compliance."},
                    {"title": "Documentation Management", "desc": "Maintain Access to Finance trackers and records to ensure alignment with program and donor requirements."},
                ],
            },
            {
                "id": _new_id(),
                "role": "Programs Assistant",
                "org": "Coalition on Violence Against Women (COVAW)",
                "location": "Nairobi, Kenya",
                "start": "2024-07-03",
                "end": "2025-09-26",
                "tags": ["programs", "communications"],
                "highlights": [
                    {"title": "Program Execution", "desc": "Coordinated program planning, budgeting, and field implementation across GBV response initiatives and economic empowerment projects."},
                    {"title": "Monitoring & Evaluation", "desc": "Conducted field monitoring visits, evaluated output data, and refined narrative reports to capture measurable outcomes."},
                    {"title": "Advocacy & Digital Communications", "desc": "Developed and deployed digital campaign messaging across COVAW platforms, improving organizational visibility and engagement."},
                    {"title": "Resource Development", "desc": "Co-authored communication toolkits and advocacy manuals; conducted needs assessments for survivors of GBV and women in informal sectors."},
                ],
            },
            {
                "id": _new_id(),
                "role": "Communications and Advocacy Intern",
                "org": "Transparency International Kenya (TI-Kenya)",
                "location": "Nairobi, Kenya",
                "start": "2023-09-01",
                "end": "2024-02-29",
                "tags": ["communications", "digital"],
                "highlights": [
                    {"title": "Media & Event Management", "desc": "Facilitated institutional public forums, advocacy workshops, and media pressers; drafted synthesis reports, minutes, and press kits."},
                    {"title": "Stakeholder Mapping & Coalition Building", "desc": "Identified and mapped strategic civil society partners, fostering coalition building for joint accountability initiatives."},
                    {"title": "Digital Advocacy & Monitoring", "desc": "Managed daily social media operations and conducted media monitoring to track anti-corruption coverage across national outlets."},
                ],
            },
            {
                "id": _new_id(),
                "role": "Advocacy and Engagement Intern",
                "org": "Twaweza East Africa",
                "location": "Nairobi, Kenya",
                "start": "2022-07-04",
                "end": "2022-12-23",
                "tags": ["communications", "knowledge"],
                "highlights": [
                    {"title": "Event Coordination", "desc": "Coordinated partner outreach, invitations, and venue logistics for the flagship Sauti initiative launch."},
                    {"title": "Database & Knowledge Archival", "desc": "Overhauled Twaweza's master media contact database; categorized physical and digital library collections using standardized information science protocols."},
                    {"title": "Content Creation & Transcription", "desc": "Produced multi-media content for digital platforms and transcribed public policy discussions on service delivery."},
                ],
            },
            {
                "id": _new_id(),
                "role": "Digital Marketing Virtual Assistant",
                "org": "Upwork Digital",
                "location": "Remote",
                "start": "2022-01-10",
                "end": "2022-05-27",
                "tags": ["digital"],
                "highlights": [
                    {"title": "Content Strategy & Design", "desc": "Designed visual branding assets in Canva and scheduled cross-platform social media content calendars."},
                    {"title": "Automation & CMS", "desc": "Managed Mailchimp email campaigns to boost lead conversion; updated web content via WordPress and tracked KPIs with Google Analytics."},
                ],
            },
            {
                "id": _new_id(),
                "role": "Data Entry & Records Clerk",
                "org": "Kericho County Government",
                "location": "Kericho, Kenya",
                "start": "2021-06-02",
                "end": "2021-12-18",
                "tags": ["knowledge"],
                "highlights": [
                    {"title": "Digitization & Registry Optimization", "desc": "Spearheaded digital migration of legacy birth/death records; recommended filing system modifications that improved departmental efficiency."},
                ],
            },
            {
                "id": _new_id(),
                "role": "Communications & Archiving Attaché",
                "org": "Kenya Electricity Generating Company Ltd (KenGen)",
                "location": "Naivasha, Kenya",
                "start": "2019-05-06",
                "end": "2019-07-30",
                "tags": ["communications", "knowledge"],
                "highlights": [
                    {"title": "Editorial & Cataloging", "desc": "Designed and published internal weekly newsletters; cataloged, classified, and indexed library materials for stakeholder retrieval."},
                ],
            },
        ],
        "projects": [
            {
                "id": _new_id(),
                "title": "Bahari Boost Challenge Fund — Access to Finance Support",
                "org": "TechnoServe",
                "period": "2026 – Present",
                "summary": "Support grant administration, due diligence, and monitoring & reporting for the "
                           "Bahari Boost Challenge Fund, a blue-economy grant facility for youth-led coastal "
                           "enterprises under TechnoServe's BlueBiz program.",
                "tags": ["programs"],
                "links": [
                    {"label": "TechnoServe Kenya", "url": "https://www.technoserve.org/region/kenya/"},
                    {"label": "Blue Economy Program Overview", "url": "https://www.technoserve.org/blog/sustainable-blue-economy-kenya/"},
                ],
            },
            {
                "id": _new_id(),
                "title": "GBV Response & Economic Empowerment Programming",
                "org": "Coalition on Violence Against Women (COVAW)",
                "period": "2024 – 2025",
                "summary": "Coordinated program planning and field monitoring for gender-based violence response "
                           "initiatives; co-authored communication toolkits and advocacy manuals for survivors "
                           "and women in informal sectors.",
                "tags": ["programs", "communications"],
                "links": [
                    {"label": "COVAW", "url": "https://covaw.or.ke/"},
                    {"label": "COVAW Publications & Resources", "url": "https://covaw.or.ke/media-centre/publications-resources/"},
                ],
            },
            {
                "id": _new_id(),
                "title": "Anti-Corruption Advocacy & Media Engagement",
                "org": "Transparency International Kenya (TI-Kenya)",
                "period": "2023 – 2024",
                "summary": "Facilitated public forums and advocacy workshops, managed social media advocacy, and "
                           "conducted media monitoring in support of TI-Kenya's governance and accountability "
                           "initiatives.",
                "tags": ["communications", "digital"],
                "links": [
                    {"label": "Transparency International Kenya", "url": "https://tikenya.org/"},
                ],
            },
            {
                "id": _new_id(),
                "title": "Sauti Launch & Stakeholder Engagement",
                "org": "Twaweza East Africa",
                "period": "2022",
                "summary": "Coordinated the launch of Twaweza's flagship Sauti citizen-voice initiative — partner "
                           "outreach, media mobilization, and knowledge archival of the master media contact "
                           "database.",
                "tags": ["communications", "knowledge"],
                "links": [
                    {"label": "Twaweza East Africa", "url": "https://twaweza.org/"},
                ],
            },
            {
                "id": _new_id(),
                "title": "Digital Marketing & Brand Content",
                "org": "Upwork Digital (Freelance)",
                "period": "2022",
                "summary": "Delivered social media content calendars, email marketing automation, and web "
                           "analytics reporting for client brands as a remote digital marketing virtual "
                           "assistant.",
                "tags": ["digital"],
                "links": [],
            },
        ],
        "competencies": [
            {"id": _new_id(), "category": "Grant & Program Support", "icon": "shield-check",
             "items": ["Due Diligence", "M&E Reporting", "Application Screening", "Compliance Tracking", "Risk Mapping"]},
            {"id": _new_id(), "category": "Strategic Communications", "icon": "megaphone",
             "items": ["Media Relations", "Press Kits", "Public Forums", "Advocacy Campaigns", "Stakeholder Mapping"]},
            {"id": _new_id(), "category": "Digital Media & Design", "icon": "camera",
             "items": ["Social Media Strategy", "Canva", "Adobe Creative Suite", "AI Utilization"]},
            {"id": _new_id(), "category": "Knowledge Governance", "icon": "book-open",
             "items": ["Archiving", "Cataloging", "Records Classification", "Database Optimization", "CMS (WordPress)", "Web Analytics (Google Analytics)"]},
            {"id": _new_id(), "category": "Cross-Cutting Areas", "icon": "heart",
             "items": ["Gender & Social Inclusion (GESI)", "Gender-Transformative Programming", "Policy Advocacy"]},
        ],
        "skills": [
            {"id": _new_id(), "name": "Communication & Advocacy", "level": 95, "group": "communications"},
            {"id": _new_id(), "name": "Media, Stakeholder & Public Relations", "level": 90, "group": "communications"},
            {"id": _new_id(), "name": "Social Media Management & Content Creation", "level": 92, "group": "digital"},
            {"id": _new_id(), "name": "Digital Marketing", "level": 85, "group": "digital"},
            {"id": _new_id(), "name": "Graphic Design (Canva, Adobe Suite)", "level": 88, "group": "digital"},
            {"id": _new_id(), "name": "CMS & Web Analytics (WordPress, GA, Mailchimp)", "level": 80, "group": "digital"},
            {"id": _new_id(), "name": "Program & Project Management", "level": 87, "group": "programs"},
            {"id": _new_id(), "name": "M&E / Reporting", "level": 85, "group": "programs"},
            {"id": _new_id(), "name": "Due Diligence & Compliance", "level": 82, "group": "programs"},
            {"id": _new_id(), "name": "Records Management & Archiving", "level": 90, "group": "knowledge"},
            {"id": _new_id(), "name": "Organization & Analytical Skills", "level": 90, "group": "knowledge"},
            {"id": _new_id(), "name": "Photography", "level": 75, "group": "digital"},
        ],
        "education": [
            {
                "id": _new_id(),
                "degree": "Bachelor of Science in Information Science and Knowledge Management",
                "school": "University of Kabianga, Kenya",
                "start": "2016-08-22",
                "end": "2020-12-10",
                "detail": "Specialization: Communications, Publishing, and Media Studies. Conferred Degree with Honors (24 March 2021).",
            },
        ],
        "certifications": [
            {
                "id": _new_id(),
                "name": "Certificate in Gender Transformative Programming",
                "issuer": "African Population and Health Research Center (APHRC)",
                "date": "2025-10-10",
                "detail": "Advanced strategies for addressing gender-based violence (GBV) and embedding gender equity into development programming.",
            },
        ],
        "references": [
            {"id": _new_id(), "name": "Mr. Samuel Ogeda", "title": "Business Development Coordinator", "org": "Transparency International Kenya"},
            {"id": _new_id(), "name": "Josiah Wandera", "title": "Research & Learning Officer", "org": "Twaweza East Africa"},
            {"id": _new_id(), "name": "Sarah Mwangi", "title": "Program & Engagement Officer", "org": "Twaweza East Africa"},
        ],
        "auth": {
            "username": DEFAULT_ADMIN_USERNAME,
            "password_hash": generate_password_hash(DEFAULT_ADMIN_PASSWORD),
        },
    }


def get_secret_key() -> str:
    with _lock:
        if os.path.exists(SECRET_KEY_PATH):
            with open(SECRET_KEY_PATH, "r", encoding="utf-8") as f:
                key = f.read().strip()
                if key:
                    return key
        key = secrets.token_hex(32)
        with open(SECRET_KEY_PATH, "w", encoding="utf-8") as f:
            f.write(key)
        return key


def get_content() -> dict:
    with _lock:
        if not os.path.exists(DATA_PATH):
            content = _default_content()
            _write(content)
            return content
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            content = json.load(f)
        # Backfill any keys introduced by newer versions of this file (e.g. a
        # new "projects" collection) without touching existing edited content.
        missing = [key for key in _default_content() if key not in content]
        if missing:
            defaults = _default_content()
            for key in missing:
                content[key] = defaults[key]
            _write(content)
        return content


def save_content(content: dict) -> None:
    with _lock:
        _write(content)


def _write(content: dict) -> None:
    tmp_path = DATA_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, DATA_PATH)


def new_id() -> str:
    return _new_id()


def tags_dict(content: dict) -> dict:
    return {t["key"]: t["label"] for t in content["tags"]}


def _parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date() if value else None


def _months_between(start: date, end: date) -> int:
    return (end.year - start.year) * 12 + (end.month - start.month) + 1


def _fmt_duration(months: int) -> str:
    years, rem = divmod(months, 12)
    parts = []
    if years:
        parts.append(f"{years} yr{'s' if years != 1 else ''}")
    if rem:
        parts.append(f"{rem} mo{'s' if rem != 1 else ''}")
    return " ".join(parts) if parts else "< 1 mo"


def enrich_experience(content: dict):
    """Return experience entries with display strings, sorted newest-first."""
    today = date.today()
    labels = tags_dict(content)
    rows = []
    for item in content["experience"]:
        start = _parse_date(item["start"])
        end = _parse_date(item.get("end"))
        effective_end = end or today
        months = _months_between(start, effective_end)
        rows.append({
            **item,
            "start_label": start.strftime("%b %Y"),
            "end_label": "Present" if end is None else end.strftime("%b %Y"),
            "duration_label": _fmt_duration(months),
            "months": months,
            "tag_labels": [labels.get(t, t) for t in item.get("tags", [])],
        })
    rows.sort(key=lambda r: r["start"], reverse=True)
    return rows


def enrich_projects(content: dict):
    labels = tags_dict(content)
    return [
        {**item, "tag_labels": [labels.get(t, t) for t in item.get("tags", [])]}
        for item in content["projects"]
    ]


def format_date(value, fmt="%b %Y") -> str:
    d = _parse_date(value)
    return d.strftime(fmt) if d else ""


def enrich_education(content: dict):
    return [
        {**item, "start_label": format_date(item["start"]), "end_label": format_date(item["end"])}
        for item in content["education"]
    ]


def enrich_certifications(content: dict):
    return [
        {**item, "date_label": format_date(item["date"], "%B %Y")}
        for item in content["certifications"]
    ]


def build_stats(content: dict) -> dict:
    experience = content["experience"]
    if experience:
        first_start = min(_parse_date(item["start"]) for item in experience)
        total_months = _months_between(first_start, date.today())
        years_span = round(total_months / 12, 1)
    else:
        years_span = 0
    orgs = {item["org"] for item in experience}
    return {
        "years_experience": years_span,
        "organizations": len(orgs),
        "roles_held": len(experience),
        "competency_areas": len(content["competencies"]),
    }
