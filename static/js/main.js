(() => {
  "use strict";

  document.getElementById("year").textContent = new Date().getFullYear();

  /* ---------- Theme toggle ---------- */
  const root = document.documentElement;
  const themeToggle = document.getElementById("themeToggle");
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme) root.setAttribute("data-theme", savedTheme);
  themeToggle.addEventListener("click", () => {
    const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
  });

  /* ---------- Mobile nav ---------- */
  const navToggle = document.getElementById("navToggle");
  const navLinks = document.getElementById("navLinks");
  navToggle.addEventListener("click", () => {
    const open = navLinks.classList.toggle("open");
    navToggle.classList.toggle("open", open);
    navToggle.setAttribute("aria-expanded", String(open));
  });
  navLinks.querySelectorAll(".nav-link").forEach((link) =>
    link.addEventListener("click", () => {
      navLinks.classList.remove("open");
      navToggle.classList.remove("open");
    })
  );

  /* ---------- Scroll progress bar ---------- */
  const progressBar = document.getElementById("scrollProgress");
  const onScroll = () => {
    const h = document.documentElement;
    const scrolled = h.scrollTop / (h.scrollHeight - h.clientHeight || 1);
    progressBar.style.width = `${Math.min(scrolled * 100, 100)}%`;

    const backToTop = document.getElementById("backToTop");
    backToTop.classList.toggle("visible", h.scrollTop > 500);
  };
  document.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  document.getElementById("backToTop").addEventListener("click", () =>
    window.scrollTo({ top: 0, behavior: "smooth" })
  );

  /* ---------- Scrollspy for nav links ---------- */
  const sections = [...document.querySelectorAll("main section[id]")];
  const navByHash = new Map(
    [...document.querySelectorAll(".nav-link")].map((a) => [a.getAttribute("href"), a])
  );
  const spy = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        const link = navByHash.get(`#${entry.target.id}`);
        if (!link) return;
        if (entry.isIntersecting) {
          navByHash.forEach((l) => l.classList.remove("active"));
          link.classList.add("active");
        }
      });
    },
    { rootMargin: "-40% 0px -55% 0px" }
  );
  sections.forEach((s) => spy.observe(s));

  /* ---------- Reveal-on-scroll ---------- */
  const revealObserver = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          obs.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );
  document.querySelectorAll(".reveal").forEach((el) => revealObserver.observe(el));

  /* ---------- Animated stat counters ---------- */
  const animateCount = (el) => {
    const target = parseFloat(el.dataset.count);
    const decimals = parseInt(el.dataset.decimals || "0", 10);
    const duration = 1200;
    const start = performance.now();
    const step = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = (target * eased).toFixed(decimals);
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };
  const statObserver = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          animateCount(entry.target);
          obs.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.5 }
  );
  document.querySelectorAll(".stat-number").forEach((el) => statObserver.observe(el));

  /* ---------- Animated skill bars ---------- */
  const fillBar = (el) => {
    const level = el.dataset.level;
    requestAnimationFrame(() => { el.style.width = `${level}%`; });
  };
  const skillObserver = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          fillBar(entry.target);
          obs.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.4 }
  );
  document.querySelectorAll(".skill-fill").forEach((el) => skillObserver.observe(el));

  /* ---------- Live experience filtering via Flask API ---------- */
  const filterBar = document.getElementById("filterBar");
  const timeline = document.getElementById("timeline");
  const emptyState = document.getElementById("emptyState");

  const escapeHtml = (str) =>
    str.replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));

  const renderTimeline = (jobs) => {
    if (!jobs.length) {
      timeline.innerHTML = "";
      emptyState.hidden = false;
      return;
    }
    emptyState.hidden = true;
    timeline.innerHTML = jobs
      .map(
        (job, i) => `
      <article class="timeline-item reveal visible" data-tags="${job.tags.join(",")}" style="--delay:${i * 40}ms">
        <div class="timeline-dot"></div>
        <div class="timeline-card">
          <div class="timeline-card-head">
            <div>
              <h3>${escapeHtml(job.role)}</h3>
              <p class="org">${escapeHtml(job.org)}</p>
            </div>
            <div class="timeline-meta">
              <span class="date-range">${escapeHtml(job.start_label)} – ${escapeHtml(job.end_label)}</span>
              <span class="duration">${escapeHtml(job.duration_label)}</span>
              <span class="loc"><svg class="icon meta-icon" viewBox="0 0 24 24"><use href="#icon-map-pin"></use></svg>${escapeHtml(job.location)}</span>
            </div>
          </div>
          <div class="tag-chips">
            ${job.tag_labels.map((l) => `<span class="chip">${escapeHtml(l)}</span>`).join("")}
          </div>
          <ul class="highlights">
            ${job.highlights
              .map((h) => `<li><strong>${escapeHtml(h.title)}:</strong> ${escapeHtml(h.desc)}</li>`)
              .join("")}
          </ul>
        </div>
      </article>`
      )
      .join("");
  };

  const cache = new Map();
  const loadExperience = async (tag) => {
    if (cache.has(tag)) {
      renderTimeline(cache.get(tag));
      return;
    }
    timeline.style.opacity = "0.4";
    try {
      const res = await fetch(`/api/experience?tag=${encodeURIComponent(tag)}`);
      const jobs = await res.json();
      cache.set(tag, jobs);
      renderTimeline(jobs);
    } catch (err) {
      console.error("Failed to load experience:", err);
    } finally {
      timeline.style.opacity = "1";
    }
  };

  if (filterBar) {
    filterBar.addEventListener("click", (e) => {
      const btn = e.target.closest(".filter-btn");
      if (!btn) return;
      filterBar.querySelectorAll(".filter-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      loadExperience(btn.dataset.tag);
    });
  }
})();
