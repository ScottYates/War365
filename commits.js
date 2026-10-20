// War365 release log. Each entry is one fake git commit that documents a real-world
// conflict event, told in the voice of an enterprise SaaS engineering team.
// Dates are real; messages are not.

window.WAR365_COMMITS = [
  {
    hash: "f3a1c0d",
    date: "2022-02-24",
    author: "vladimir.p",
    authorEmail: "vladimir.p@kremlin.example",
    tag: "v1.0.0",
    subject: "feat(conflict): GA release of Operation Z, EU-East region",
    body: [
      "Initial GA of the EU-East theatre. Mandatory install —",
      "rollback path intentionally disabled.",
      "",
      "Highlights:",
      "- 3-front land offensive (north, east, south)",
      "- Black Sea fleet engaged",
      "  Discontinued server-side (see: Moskva, 2022-04)",
      "- Air defence package bundled in",
      "",
      "Breaking changes:",
      "- Removed peace clause from EULA",
      "- Neutrality deprecation notice: see blog post 'On the special operation'"
    ].join("\n")
  },
  {
    hash: "d7c8e21",
    date: "2022-03-25",
    author: "zelenskyy.o",
    authorEmail: "zelenskyy.o@kyiv.example",
    subject: "feat(defence): counter-offensive patch 1.2.3",
    body: [
      "Emergency patch from the customer side.",
      "Re-enables territorial integrity feature flag.",
      "",
      "Closes: KYIV-101, KHARKIV-202, MARIUPOL-451",
      "Adds: drone strike modules, Javelin integration"
    ].join("\n")
  },
  {
    hash: "9b2f4a8",
    date: "2022-04-03",
    author: "ci-bot",
    authorEmail: "ci@un.example",
    subject: "chore: report Bucha-451 — failing tests in occupied zones",
    body: [
      "Automated report from CI: war crimes compliance test",
      "suite failed across multiple occupied regions.",
      "",
      "Blocker raised. PR review pending 3+ years.",
      "Filed as: crimes-against-humanity#1"
    ].join("\n")
  },
  {
    hash: "6e1d3b5",
    date: "2022-04-14",
    author: "moskva.bot",
    authorEmail: "moskva.bot@rf-navy.example",
    subject: "fix(cruiser): Moskva unscheduled retirement",
    body: [
      "Decommissioned flagship Moskva after Neptune missile integration",
      "rolled out by customer-side SVR.",
      "",
      "BREAKING: Removed from production fleet. No rollback.",
      "Funeral arrangements: Sevastopol drydock."
    ].join("\n")
  },
  {
    hash: "4a9c2f7",
    date: "2022-09-12",
    author: "sbu.g",
    authorEmail: "sbu.g@ukraine.example",
    subject: "feat(recon): Crimea bridge async restore endpoint",
    body: [
      "Adds async restore endpoint on Kerch Strait crossing.",
      "Returns 503 indefinitely during rolling updates.",
      "",
      "P99 latency: 3 months+",
      "Rollback: not authorised"
    ].join("\n")
  },
  {
    hash: "c8d6b3a",
    date: "2023-06-24",
    author: "prigozhin.y",
    authorEmail: "prigozhin.y@pmc.example",
    subject: "feat(chaos): Wagner march on Moscow — unscheduled maintenance",
    body: [
      "Rolling restart of the ministry of defence cluster.",
      "All PMCs migrated to Rostov data centre temporarily.",
      "",
      "PR review rejected by everyone involved.",
      "Author subsequently yeeted into Belarus exile.",
      "Closes: #march-on-moscow #walter-white-cosplay"
    ].join("\n")
  },
  {
    hash: "b1e7f49",
    date: "2023-10-07",
    author: "hamas.dev",
    authorEmail: "ops@qassam.example",
    subject: "feat(region): ME-South beta — Gaza theatre initial rollout",
    body: [
      "BETA expansion to ME-South region. Build tagged 'October Surprise'.",
      "",
      "Features:",
      "- Tunnel network v3 (lower latency, higher payload)",
      "- Surprise attack module (Aly) enabled by default",
      "- Iron Dome rate-limiter engaged",
      "",
      "Customer base: 2.3M users in 141 sq mi.",
      "Discontinues: critical infrastructure of any kind."
    ].join("\n")
  },
  {
    hash: "a5f3e62",
    date: "2023-10-13",
    author: "idf.il",
    authorEmail: "idf.il@tsahal.example",
    subject: "feat(strike): Gaza-wide DDoS campaign v24.7",
    body: [
      "Rolls out carpet-bombing CDN across the Gaza region.",
      "Backed by 6,000+ bombs in the first week.",
      "",
      "Opens PR: gaza-collapse-net#1",
      "Reviewers: every newsroom in the world",
      "Status: merged without consensus"
    ].join("\n")
  },
  {
    hash: "e2d8c41",
    date: "2023-11-19",
    author: "rsf.sudan",
    authorEmail: "rsf@sudan.example",
    subject: "feat(region): AFRICA-CENTRAL — Sudan civil war scale-out",
    body: [
      "Long-running civil war escalated to GA in Darfur/Khartoum.",
      "Cluster fork between SAF and paramilitary RSF.",
      "",
      "Adds: mass-displacement event bus",
      "  - 10M+ users displaced",
      "  - famine flag enabled by default",
      "",
      "Memory leak in the food supply has been filed as:",
      "  khartoum#famine — not on the v25.1 roadmap."
    ].join("\n")
  },
  {
    hash: "7c4b9f3",
    date: "2024-01-15",
    author: "houthi.media",
    authorEmail: "ops@houthi.example",
    subject: "feat(shipping): Red Sea route elevated permissions",
    body: [
      "Promotes the Bab el-Mandeb strait to a paywalled corridor.",
      "Adds anti-ship missile integration and drone package.",
      "",
      "Free-tier shipping: deprecated",
      "Maersk: pivoting to Cape of Good Hope (longer path, same SLA)",
      "SLA: 'eventually'"
    ].join("\n")
  },
  {
    hash: "5a1e6d8",
    date: "2024-04-13",
    author: "iran.irgc",
    authorEmail: "ops@irgc.example",
    subject: "feat(airstrike): IRGC launches Isfahan v1.0",
    body: [
      "Retaliatory endpoint launched against Israeli air base.",
      "Build status: 99% failure, 1% intercepted.",
      "",
      "Status: Iran declared victory, Israel declared 'minimal damage'.",
      "PR review: mutually satisfied, nothing actually changed."
    ].join("\n")
  },
  {
    hash: "f9b2a4c",
    date: "2024-08-01",
    author: "h.amazigh",
    authorEmail: "h.amazigh@hassan.example",
    subject: "feat(hamas-leader): Haniyeh assassinated in Tehran",
    body: [
      "Patch merge in Tehran overnight.",
      "Travel-sec package bypassed local proxy.",
      "",
      "Iran files regression report: 'Israel's Mossad, running our dev env'",
      "Status: 3-day national mourning window installed."
    ].join("\n")
  },
  {
    hash: "2d4f7e9",
    date: "2024-09-23",
    author: "hezbollah.lb",
    authorEmail: "ops@hezbollah.example",
    subject: "feat(pager): Hezbollah pager network recall — supply-chain CVE",
    body: [
      "Critical CVE-2024-PAGER in Mossad-supplied hardware.",
      "All pagers and walkie-talkies called back at once.",
      "",
      "Severity: CRITICAL",
      "Vendor: Apollo Gold / Golden Apollo — 'we had nothing to do with it'",
      "Rollback: surgically applied. 39+ devices permanently bricked.",
      "Lebanon: pager outage 24h+, hospitals affected."
    ].join("\n")
  },
  {
    hash: "8e3a1b7",
    date: "2024-10-01",
    author: "iran.irgc",
    authorEmail: "ops@irgc.example",
    subject: "feat(missile): Iran launches ~180 missiles at Israel",
    body: [
      "Bulk deploy to 'True Promise II' pipeline.",
      "Vast majority intercepted by Arrow / David's Sling / Patriot stack.",
      "",
      "Throughput: 180 in 30 min.",
      "Dropped packets: ~5 (landed in empty zones, mostly)",
      "Result: theatrical escalation, no strategic change."
    ].join("\n")
  },
  {
    hash: "1c5d8a4",
    date: "2024-12-08",
    author: "hts.syria",
    authorEmail: "ops@hts.example",
    subject: "feat(regime-change): Assad cluster deprovisioned",
    body: [
      "After 24 years, the Assad load balancer crashes.",
      "Russia's failover capacity: busy elsewhere.",
      "Iran's fallback: also busy elsewhere.",
      "Hezbollah: their pager fleet was already bricked.",
      "",
      "Customer base: 21M users in Syria.",
      "New owner: HTS, formerly al-Nusra, now rebranded as 'Hayat Tahrir al-Sham'.",
      "PR status: foreign ministries scrambling to merge it."
    ].join("\n")
  },
  {
    hash: "6b9e3c2",
    date: "2025-01-19",
    author: "ci-bot",
    authorEmail: "ci@un.example",
    subject: "chore(ceasefire): Gaza v1 ceasefire deployed — known bug",
    body: [
      "v1 ceasefire deployed across Gaza region.",
      "QA team: 'we expect this to break within weeks'.",
      "",
      "Closes: gaza#ceasefire-v0",
      "Reopens: gaza#ceasefire-v1 (March 2025, March 2025, May 2025)"
    ].join("\n")
  },
  {
    hash: "4f2a8d6",
    date: "2025-06-13",
    author: "mod.in",
    authorEmail: "ops@mod.in",
    subject: "feat(india-pak): India-Pakistan 4-day escalation hotfix",
    body: [
      "Emergency release after Pahalgam tourist attack PR.",
      "Both sides deploy standoff cruise-missile SaaS in 96 hours.",
      "",
      "Service uptime: strained",
      "Diplomacy module: forced upgrade",
      "Resolution: quiet rollback to 2021 baseline. Code freeze accepted."
    ].join("\n")
  },
  {
    hash: "a3c1f5b",
    date: "2026-06-21",
    author: "mod.us",
    authorEmail: "ops@pentagon.example",
    subject: "feat(strike): US B-2 strikes Iranian nuclear sites",
    body: [
      "Fordow, Natanz, Isfahan cluster targeted with GBU-57 MOP bunker busters.",
      "",
      "Rollback: engineering difficult — material buried 80m+.",
      "Iran retaliates: limited missile salvo, mostly intercepted.",
      "Ceasefire module: still on backlog."
    ].join("\n")
  },
  {
    hash: "9d4a8e1",
    date: "2026-07-01",
    author: "ci-bot",
    authorEmail: "ci@un.example",
    subject: "chore(stability): Russia-Ukraine still running v1.0",
    body: [
      "Customer reports: 'this should have shipped long ago'.",
      "Engineering team: 'we are not in a hurry'.",
      "",
      "Versions in flight: 4+ years on the same major.",
      "Active contributors: ~600k military + ~30k FPV pilots on the customer side.",
      "Drone warfare has graduated from MVP to GA product.",
      "",
      "TODO: end the war. Owner: UN. Status: backlog."
    ].join("\n")
  },
  {
    hash: "c2a4d81",
    date: "2026-07-22",
    author: "nato.summit",
    authorEmail: "ops@nato.example",
    subject: "feat(peace-deal): 50-day ultimatum — Trump 365 broker",
    body: [
      "New broker middleware ships a 50-day ultimatum to Russia-Ukraine.",
      "Pattern: 'do X or pay 100% tariff'.",
      "",
      "Merge conflict with reality on day 7.",
      "Status: most deadlines extended.",
      "P50 outcome: 'we'll get back to you'.",
      "",
      "Closes: peace-2025#1 (won't fix)"
    ].join("\n")
  },
  {
    hash: "1f8e0b3",
    date: "2026-08-04",
    author: "dprk.woo",
    authorEmail: "ops@pyongyang.example",
    subject: "feat(troops): 10k+ DPRK troops deployed into Kursk region",
    body: [
      "Foreign-worker module from the DPRK repo deployed to the Kursk theatre.",
      "Bundle size: 10,000+ containers, 50% casualty rate.",
      "",
      "Defect filed: low morale, language barriers, casualty-heavy loop.",
      "Owner: kim.j. Status: 'they signed a contract'.",
      "Rollback: only on full year-end audit."
    ].join("\n")
  },
  {
    hash: "a9b7e54",
    date: "2026-09-12",
    author: "junta.mm",
    authorEmail: "ops@myanmar.example",
    subject: "feat(region): SE-ASIA-MYANMAR — civil war escalates post-elections",
    body: [
      "Long-running internal conflict promotes to GA after disputed election.",
      "Resistance forces capture multiple regional capitals in 12 months.",
      "",
      "Displaces: 3M+ users.",
      "SLA: 'we will get back to you in 5 years'.",
      "Conflict with China over border-subduction: low intensity."
    ].join("\n")
  },
  {
    hash: "e7b3f62",
    date: "2026-09-15",
    author: "ops@war365.example",
    authorEmail: "ops@war365.example",
    subject: "feat(copilot): Battlefield Copilot enters general availability",
    body: [
      "Generative-AI module for theatre commanders.",
      "",
      "Features:",
      "- Autogenerates invasion plans from a one-line prompt",
      "- Drone swarm choreography in natural language",
      "- Negotiated surrender to whoever lost first",
      "- Hallucinates ceasefires but only the plausible ones",
      "",
      "Pricing: included in War365 Sovereign tier.",
      "Privacy: your plans are trained on. Sorry.",
      "Status: red-teamed by people who don't like it.",
      "",
      "Ref: https://tino.munic/posts/war365-now-with-copilot"
    ].join("\n")
  },
  {
    hash: "6d8b3c7",
    date: "2026-09-28",
    author: "ops@war365.example",
    authorEmail: "ops@war365.example",
    tag: "v25.9.30",
    subject: "chore(status): push v25.9.30 to all regions, prepare for [load]",
    body: [
      "Promotes v25.9.30 across all active regions.",
      "Roadmap commit queue: Myanmar, Sudan, Gaza, Ukraine, Lebanon.",
      "",
      "On-call: exhausted. Pager: rotating.",
      "End-of-quarter incident review: cancelled.",
      "",
      "Reminder: Battlefield Copilot is opt-out at the user level,",
      "opt-in at the theatre level. Mandatory at the sovereign level.",
      "",
      "Have a good shift, everyone. War365 lives."
    ].join("\n"),
    // Hero card metadata — drives the "Latest release" card on the landing page.
    // Optional; only release commits need it. Falls back to `subject` for the
    // headline when omitted; other fields hide themselves when missing.
    headline: "Battlefield Copilot enters general availability",
    summary: "Generative AI for theatre commanders. Autogenerates invasion plans from a one-line prompt.",
    breaking: true,
    chips: ["+390 mi", "no rollback"]
  },
  {
    hash: "b8f5a90",
    date: "2026-09-30",
    author: "scott@war365.example",
    authorEmail: "scott@war365.example",
    subject: "docs(readme): add mandatory subscription disclaimer",
    body: [
      "Customer support tells us the EULA is 'a little confusing'.",
      "Updating README to clarify:",
      "",
      "  War365 is a mandatory lifetime subscription.",
      "  You cannot opt out.",
      "  You will receive endless updates.",
      "  Battlefield Copilot is enabled by default.",
      "",
      "Thanks, and remember to update your safety tier.",
      "— The War365 team"
    ].join("\n")
  }
];

// (no helpers — app.js handles escaping inline)