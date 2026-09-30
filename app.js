(function () {
  "use strict";

  const log = document.getElementById("commit-log");
  const filter = document.getElementById("commit-filter");

  if (!log || !window.WAR365_COMMITS) return;

  function inferType(subject) {
    const m = subject.match(/^([a-z]+)(?:\([^)]+\))?:/);
    if (!m) return "feat";
    const t = m[1].toLowerCase();
    if (["feat", "fix", "chore", "docs", "refactor", "perf", "test", "build", "ci"].includes(t)) {
      return t;
    }
    return "feat";
  }

  function escapeHtml(s) {
    return s
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function renderRow(commit) {
    const type = inferType(commit.subject);
    const subjectHtml = commit.tag
      ? `<span class="commit-tag">tag: ${escapeHtml(commit.tag)}</span>${escapeHtml(commit.subject)}`
      : escapeHtml(commit.subject);
    const bodyHtml = commit.body
      ? `<div class="commit-detail">${escapeHtml(commit.body).replace(/\n/g, "<br>")}</div>`
      : "";
    return `
      <div class="commit-row" role="listitem" data-type="${type}" data-search="${escapeHtml((commit.subject + " " + commit.author + " " + (commit.body || "")).toLowerCase())}">
        <div class="commit-gutter"><span class="commit-dot" title="${type}"></span></div>
        <div class="commit-when">${escapeHtml(commit.date)}</div>
        <div class="commit-meta">
          <span class="commit-author">${escapeHtml(commit.author)}</span>
          <span class="commit-email">${escapeHtml(commit.authorEmail)}</span>
          <span class="commit-hash">${escapeHtml(commit.hash)}</span>
        </div>
        <div class="commit-body">
          <p class="commit-subject">${subjectHtml}</p>
          ${bodyHtml ? '<button class="commit-toggle" type="button" aria-expanded="false">expand</button>' : ""}
          ${bodyHtml}
        </div>
      </div>
    `;
  }

  function render(commits) {
    if (!commits.length) {
      log.innerHTML = '<div class="commit-empty">no commits match your filter — try a different search</div>';
      return;
    }
    log.innerHTML = commits.map(renderRow).join("");

    log.querySelectorAll(".commit-toggle").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const row = e.target.closest(".commit-row");
        const open = row.classList.toggle("is-open");
        btn.setAttribute("aria-expanded", open ? "true" : "false");
        btn.textContent = open ? "collapse" : "expand";
      });
    });
  }

  // Sort by date descending (newest first), like `git log`. Returns a new
  // array — the source commits array stays in ascending chronological order
  // per AGENTS.md, and `paintStats` keeps reading `commits[length-1]` for the
  // hero "last deployment" stat.
  function sortByDateDesc(commits) {
    return commits.slice().sort((a, b) =>
      a.date < b.date ? 1 : a.date > b.date ? -1 : 0
    );
  }

  // initial render
  render(sortByDateDesc(window.WAR365_COMMITS));

  // hero stats
  (function paintStats() {
    const el = (id) => document.getElementById(id);
    const commits = window.WAR365_COMMITS;
    if (!el("stat-commits")) return;
    el("stat-commits").textContent = commits.length;
    // active theatres: regions mentioned in subjects/bodies
    const theatres = new Set();
    const re = /(Gaza|Ukraine|Sudan|Syria|Iran|Israel|Hezbollah|Houthi|Yemen|Myanmar|Haiti|Sahel|Khartoum|Russia|Lebanon|Pakistan|India)/gi;
    commits.forEach((c) => {
      const blob = (c.subject + " " + (c.body || "")).match(re);
      if (blob) blob.forEach((m) => theatres.add(m.toLowerCase()));
    });
    el("stat-theatres").textContent = theatres.size;
    const latest = commits[commits.length - 1];
    el("stat-last").textContent = latest ? latest.date : "—";
    // Hero card: drive from the latest commit with a `tag` field, walking
    // backwards. Post-release commits (e.g. a docs update shipped after
    // v25.9.30) never override the hero, so the card always advertises the
    // most recent release rather than the most recent commit.
    let release = null;
    for (let i = commits.length - 1; i >= 0; i--) {
      if (commits[i].tag) { release = commits[i]; break; }
    }
    if (!release) release = latest;

    const heroTag = el("hero-tag");
    if (heroTag) {
      heroTag.textContent = release && release.tag ? `tag: ${release.tag}` : "tag: —";
    }

    const heroHeadline = el("hero-headline");
    if (heroHeadline) {
      heroHeadline.textContent = (release && (release.headline || release.subject)) || "—";
    }

    const heroSummary = el("hero-summary");
    if (heroSummary) {
      if (release && release.summary) {
        heroSummary.textContent = release.summary;
        heroSummary.hidden = false;
      } else {
        heroSummary.hidden = true;
      }
    }

    const heroChips = el("hero-chips");
    if (heroChips) {
      const parts = [];
      if (release && release.breaking) {
        parts.push('<span class="chip chip-red">BREAKING</span>');
      }
      if (release && Array.isArray(release.chips)) {
        release.chips.forEach((c) => {
          parts.push('<span class="chip">' + escapeHtml(String(c)) + '</span>');
        });
      }
      heroChips.innerHTML = parts.join("");
    }
  })();

  // filter
  filter.addEventListener("input", (e) => {
    const q = e.target.value.trim().toLowerCase();
    if (!q) return render(sortByDateDesc(window.WAR365_COMMITS));
    const filtered = window.WAR365_COMMITS.filter((c) =>
      c.subject.toLowerCase().includes(q) ||
      c.author.toLowerCase().includes(q) ||
      (c.body || "").toLowerCase().includes(q)
    );
    render(sortByDateDesc(filtered));
  });

  // expand-on-hover for desktop, click for touch (optional nicety)
  log.querySelectorAll(".commit-row").forEach((row) => {
    row.addEventListener("dblclick", () => {
      const btn = row.querySelector(".commit-toggle");
      if (btn) btn.click();
    });
  });
})();