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

  // initial render
  render(window.WAR365_COMMITS);

  // filter
  filter.addEventListener("input", (e) => {
    const q = e.target.value.trim().toLowerCase();
    if (!q) return render(window.WAR365_COMMITS);
    const filtered = window.WAR365_COMMITS.filter((c) =>
      c.subject.toLowerCase().includes(q) ||
      c.author.toLowerCase().includes(q) ||
      (c.body || "").toLowerCase().includes(q)
    );
    render(filtered);
  });

  // expand-on-hover for desktop, click for touch (optional nicety)
  log.querySelectorAll(".commit-row").forEach((row) => {
    row.addEventListener("dblclick", () => {
      const btn = row.querySelector(".commit-toggle");
      if (btn) btn.click();
    });
  });
})();